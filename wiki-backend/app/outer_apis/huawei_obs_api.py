import asyncio
import mimetypes
import uuid
from typing import Optional, Dict, Any

from app.core.logging_config import setup_logging
from config import settings
logger = setup_logging()

class HuaweiOBSClient:
    """华为OBS 客户端封装

    提供创建/删除桶、获取桶列表、上传/删除对象的异步接口。
    基于华为官方 Python SDK: esdk-obs-python (模块名: obs)。
    技术支持使用桶名：support-fae
    """

    def __init__(
        self,
        access_key_id: str = settings.OBS_ACCESS_KEY_ID,
        secret_access_key: str = settings.OBS_SECRET_ACCESS_KEY,
        endpoint: str = settings.OBS_ENDPOINT,
        bucket_name: str = settings.OBS_BUCKET_NAME,
        is_secure: bool = True,
    ) -> None:
        self._ak = access_key_id
        self._sk = secret_access_key
        self._endpoint = endpoint
        self._is_secure = is_secure
        self._bucket_name = bucket_name
        # 懒加载 client，避免在无 SDK 场景下导入即失败
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from obs import ObsClient  # type: ignore
            except Exception as exc:  # pragma: no cover - 仅在缺少依赖时报错
                logger.error("缺少依赖: esdk-obs-python，请在 requirements.txt 中添加并安装。")
                raise exc

            self._client = ObsClient(
                access_key_id=self._ak,
                secret_access_key=self._sk,
                server=self._endpoint,
                is_secure=self._is_secure,
            )
        return self._client

    async def _to_thread(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def create_bucket(
        self, bucket_name: str, location: str = "cn-south-1", acl: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建桶

        acl 可选值参考官方 SDK（例如: 'public-read', 'private' 等）。
        """
        client = self._get_client()
        try:
            def _op():
                params = {"location": location}
                if acl:
                    params["aclControl"] = acl
                return client.createBucket(bucket_name, **params)

            resp = await self._to_thread(_op)
            if resp.status < 300:
                return {"success": True, "data": {"bucket": bucket_name, "location": location}}
            return {"success": False, "error": f"createBucket failed: status={resp.status}, reason={getattr(resp, 'reason', '')}"}
        except Exception as exc:
            logger.error(f"创建桶异常: {exc}")
            return {"success": False, "error": str(exc)}

    async def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """删除桶（桶需为空）。"""
        client = self._get_client()
        try:
            resp = await self._to_thread(client.deleteBucket, bucket_name)
            if resp.status < 300:
                return {"success": True, "data": {"bucket": bucket_name}}
            return {"success": False, "error": f"deleteBucket failed: status={resp.status}, reason={getattr(resp, 'reason', '')}"}
        except Exception as exc:
            logger.error(f"删除桶异常: {exc}")
            return {"success": False, "error": str(exc)}

    async def list_buckets(self) -> Dict[str, Any]:
        """获取当前账号下的桶列表"""
        client = self._get_client()
        try:
            resp = await self._to_thread(client.listBuckets)
            if resp.status < 300:
                buckets = []
                try:
                    body = getattr(resp, "body", None)
                    items = getattr(body, "buckets", []) if body is not None else []
                    for b in items:
                        name = getattr(b, "name", None) or getattr(b, "bucketName", None)
                        creation_date = getattr(b, "creationDate", None)
                        location = getattr(b, "location", None)
                        buckets.append(
                            {"name": name, "creationDate": creation_date, "location": location}
                        )
                except Exception:
                    # 兼容某些实现 body 可能为 dict 的情况
                    body = getattr(resp, "body", {})
                    if isinstance(body, dict):
                        for b in body.get("buckets", []):
                            buckets.append(
                                {
                                    "name": b.get("name") or b.get("bucketName"),
                                    "creationDate": b.get("creationDate"),
                                    "location": b.get("location"),
                                }
                            )
                return {"success": True, "data": buckets}
            return {"success": False, "error": f"listBuckets failed: status={resp.status}, reason={getattr(resp, 'reason', '')}"}
        except Exception as exc:
            logger.error(f"获取桶列表异常: {exc}")
            return {"success": False, "error": str(exc)}

    async def upload_file(
        self,
        object_key: str,
        file_path: str,
        public_read: bool = False,
        access_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """上传本地文件至 OBS

        access_domain: 访问域名（如 'support-fae.obs.cn-south-1.myhuaweicloud.com'）。
        若未提供，则按 https://{bucket}.{endpoint}/{object_key} 拼接。
        """
        client = self._get_client()
        try:
            normalized_key = object_key.lstrip("/")
            headers = {"x-obs-acl": "public-read"} if public_read else None
            logger.debug(f"headers: {headers}")
            resp = await self._to_thread(
                client.putFile,
                self._bucket_name,
                normalized_key,
                file_path,
                headers=headers,
            )

            if resp.status < 300:
                domain = access_domain or f"{self._bucket_name}.{self._endpoint}"
                if public_read:
                    # 再次显式设置对象ACL，避免某些场景下头部未生效
                    try:
                        await self._to_thread(client.setObjectAcl, self._bucket_name, normalized_key, aclControl='public-read')
                    except Exception as acl_exc:
                        logger.error(f"设置对象ACL为public-read失败: {acl_exc}")
                    # 公开读：返回长期有效直链
                    url = f"https://{domain}/{normalized_key}"
                else:
                    # 私有：返回短期签名链接
                    signed = await self.generate_signed_url("GET", normalized_key, expires=3600*24*3)
                    url = (signed or {}).get("data", {}).get("signed_url")
                return {"success": True, "data": {"bucket": self._bucket_name, "key": normalized_key, "url": url}}
            return {"success": False, "error": f"putFile failed: status={resp.status}, reason={getattr(resp, 'reason', '')}"}
        except Exception as exc:
            logger.error(f"上传文件异常: {exc}")
            return {"success": False, "error": str(exc)}

    async def delete_file(self, object_key: str) -> Dict[str, Any]:
        """删除对象"""
        client = self._get_client()
        try:
            normalized_key = object_key.lstrip("/")
            resp = await self._to_thread(client.deleteObject, self._bucket_name, normalized_key)
            if resp.status < 300:
                return {"success": True, "data": {"bucket": self._bucket_name, "key": normalized_key}}
            return {"success": False, "error": f"deleteObject failed: status={resp.status}, reason={getattr(resp, 'reason', '')}"}
        except Exception as exc:
            logger.error(f"删除对象异常: {exc}")
            return {"success": False, "error": str(exc)}

    async def generate_signed_url(
        self,
        method: str,
        object_key: str,
        expires: int = 3600*24*3,
    ) -> Dict[str, Any]:
        """生成对象的临时签名 URL。

        method: 请求方法，如 'GET'、'PUT'。
        object_key: 对象键。
        expires: 过期秒数。
        """
        client = self._get_client()
        try:
            normalized_key = object_key.lstrip("/")
            resp = await self._to_thread(
                client.createSignedUrl,
                method,
                self._bucket_name,
                normalized_key,
                expires=expires,
            )
            signed_url = getattr(resp, "signedUrl", None)
            if signed_url:
                return {"success": True, "data": {"signed_url": signed_url}}
            return {"success": False, "error": "failed to create signed url"}
        except Exception as exc:
            logger.error(f"生成签名URL异常: {exc}")
            return {"success": False, "error": str(exc)}

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            finally:
                self._client = None

    def __del__(self):  # 防御性清理
        try:
            self.close()
        except Exception:
            pass

