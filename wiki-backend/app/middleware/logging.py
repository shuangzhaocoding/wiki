"""
请求日志中间件
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.logging_config import setup_logging

# 初始化日志
logger = setup_logging()


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"
        
        # 记录请求头（可选，敏感信息需要过滤）
        headers = dict(request.headers)
        # 过滤敏感信息
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        filtered_headers = {k: v if k.lower() not in sensitive_headers else "***" 
                           for k, v in headers.items()}
        
        # 记录请求体（仅对POST/PUT/PATCH请求，且排除二进制/文件上传）
        body = None
        content_type = (request.headers.get("content-type") or "").lower()
        is_multipart = "multipart/form-data" in content_type
        if method in ["POST", "PUT", "PATCH"] and not is_multipart:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode("utf-8")[:500]
                    # 禁止替换 _receive：否则 BaseHTTPMiddleware + StreamingResponse
                    # 在收尾阶段会误判收到重复的 http.request。
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")
                body = None
        elif is_multipart:
            body = "<multipart/form-data>"
        
        # 记录请求参数
        query_params = dict(request.query_params)
        
        # 记录请求信息
        logger.info(
            f"📥 请求开始 | {method} {url} | "
            f"客户端: {client_host}:{client_port}"
        )
        
        if query_params:
            logger.debug(f"   查询参数: {query_params}")
        
        if body:
            logger.debug(f"   请求体: {body[:200]}...")  # 只记录前200字符
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"❌ 请求异常 | {method} {url} | "
                f"耗时: {process_time:.3f}s | 错误: {str(e)}"
            )
            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 获取响应状态码
        status_code = response.status_code
        
        # 记录响应信息
        status_emoji = "✅" if 200 <= status_code < 300 else "⚠️" if 300 <= status_code < 400 else "❌"
        logger.info(
            f"{status_emoji} 请求完成 | {method} {url} | "
            f"状态码: {status_code} | 耗时: {process_time:.3f}s"
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
