import base64
import json
import os
from config import settings
from app.outer_apis.base_api import BaseAsyncAPI
from app.core.logging_config import setup_logging
logger = setup_logging()

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Any

class NarwalTech(BaseAsyncAPI):
    def __init__(self):
        self.base_url = settings.AFTER_SALE_BASE_URL # 正式环境
        self.LOGIN_URL = self.base_url + settings.AFTER_SALE_LOGIN_URL                                         # 登录
        self.token = ""
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': "Bearer {}".format(self.token),
            'Connection': 'keep-alive'}

    async def get_res(self, url: str, headers: dict, params: Any = None):
        result = await super().get_res(url, headers, params)
        if_retry = await self.exception_handling(result)
        if if_retry:
            return await super().get_res(url, self.headers, params)
        else:
            return result
        
    async def post_res(self, url: str, headers: dict, datas: Any = None):
        result = await super().post_res(url, headers, datas)
        if_retry = await self.exception_handling(result)
        if if_retry:
            return await super().post_res(url, self.headers, datas)
        else:
            return result
        
    async def del_res(self, url: str, headers: dict, datas: Any = None):
        result = await super().del_res(url, headers)
        if_retry = await self.exception_handling(result)
        if if_retry:
            return await super().del_res(url, self.headers)
        else:
            return result
        
    async def put_res(self, url: str, headers: dict, datas: Any):
        result = await super().put_res(url, headers, datas)
        if_retry = await self.exception_handling(result)
        if if_retry:
            return await super().put_res(url, self.headers, datas)
        else:
            return result

    async def exception_handling(self, http_response: dict) -> None:
        """云鲸售后服务系统API请求异常处理方法，判断请求是否异常，遇到异常时，抛出InterruptedError异常，触发重试
        :param
            http请求返回结果
        :return
            None
        """
        # 返回状态吗4006时，售后系统请求鉴权失败，可能是token过期了，更新token并重试
        if http_response.get("code", 200) == 4006:
            logger.warning('Token过期，开始更新Token')
            await self.login()
            self.headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Authorization': "Bearer {}".format(self.token),
            }
            return True
        return False

    @staticmethod
    def aes_encrypt_password(password: str) -> str:
        """使用AES CFB模式和ISO10126Padding加密密码
        :param
            password: 明文密码
        :return
            encrypted_password: 加密后的密码(Base64编码)
        """
        key = settings.AES_KEY.encode('utf-8')
        iv = settings.AES_IV.encode('utf-8')
        
        # ISO10126Padding: 填充字节中，除最后一个字节外都是随机的，最后一个字节存储填充长度
        password_bytes = password.encode('utf-8')
        block_size = 16
        padding_length = block_size - (len(password_bytes) % block_size)
        
        # 如果数据长度刚好是block_size的倍数，仍需填充一个完整的block
        if padding_length == 0:
            padding_length = block_size
        
        # 生成随机填充字节，最后一个字节是填充长度
        random_bytes = os.urandom(padding_length - 1)
        padding = random_bytes + bytes([padding_length])
        padded_data = password_bytes + padding
        
        # 使用AES CFB模式加密
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        return base64.b64encode(encrypted).decode('utf-8')

    async def user_login(self, email: str, password: str) -> str:
        """售后系统登录验证
        :param
            email: 邮箱
            password: 帐号
        :return
            token: 鉴权token
        """
        # 使用AES加密密码
        encrypted_password = self.aes_encrypt_password(password)
        payload = {"mobile": email, "password": encrypted_password, "platId": 2}
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
        }
        result = await self.post_res(self.LOGIN_URL, headers=headers, datas=json.dumps(payload))
        logger.debug(result)
        try:
            token = result['data']['accessToken']
            return token
        except (KeyError, TypeError):
            return None

