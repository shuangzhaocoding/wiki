import os,sys
import aiohttp
import asyncio
import traceback
from app.core.logging_config import setup_logging
logger = setup_logging()

class BaseAsyncAPI(object):
    def __init__(self):
        pass

    async def get_res(self, url: str, headers: dict, params= None, timeout=30):
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.get(url=url,headers=headers, params=params ,timeout=timeout)
                    # logger.debug(res.text)
                    if res and res.status == 200:
                        # logger.debug(await res.json())
                        return await res.json()
                    logger.warning(await res.json())
                    logger.warning("请求异常，1秒后发起重试")
                    await asyncio.sleep(1)
            except:
                logger.error(url)
                logger.error(traceback.format_exc())
                await asyncio.sleep(1)

    async def post_res(self, url, headers, datas, params=None, timeout=30):
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.post(url=url, headers=headers, data=datas, params=params, timeout=timeout)
                    # logger.debug(res.request_info)
                    if res and res.status == 200:
                        # logger.debug(await res.json())
                        return await res.json()
                    elif res and res.status == 401:
                        logger.error("鉴权过期")
                        return {"code": 401, "msg": "鉴权过期"}
                    logger.warning(res.text)
                    logger.warning("请求异常，1秒后发起重试")
                    await asyncio.sleep(1)
            except:
                logger.error(url)
                logger.error(traceback.format_exc())
                await asyncio.sleep(1)

    async def put_res(self, url, headers, datas):
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.put(url=url,headers=headers, data=datas, timeout=30)
                    if res and res.status == 200:
                        logger.debug(await res.json())
                        return await res.json()
                    logger.warning(await res.json())
                    logger.warning("请求异常，1秒后发起重试")
                    await asyncio.sleep(1)
            except:
                logger.error(url)
                logger.error(traceback.format_exc())
                await asyncio.sleep(1)

    async def del_res(self, url, headers, datas = None):
        for _ in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    res = await session.delete(url=url,headers=headers, data=datas, timeout=30)
                    if res and res.status == 200:
                        logger.debug(await res.json())
                        return await res.json()
                    logger.warning(await res.json())
                    logger.warning("请求异常，1秒后发起重试")
                    await asyncio.sleep(1)
            except:
                logger.error(url)
                logger.error(traceback.format_exc())
                await asyncio.sleep(1)
