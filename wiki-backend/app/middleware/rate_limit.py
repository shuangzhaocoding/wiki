"""
限流中间件
"""
import time
from collections import defaultdict
from typing import Dict, Tuple, Optional
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.security import decode_access_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件：限制每分钟访问2次"""
    
    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests  # 最大请求数
        self.window_seconds = window_seconds  # 时间窗口（秒）
        # 存储每个标识符的访问记录: identifier -> [(timestamp1, timestamp2, ...)]
        self.requests: Dict[str, list] = defaultdict(list)
        # 清理过期记录的时间间隔（秒）
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup = time.time()
    
    def _get_identifier(self, request: Request) -> str:
        """获取请求的唯一标识符（优先使用用户ID，否则使用IP地址）"""
        # 尝试从Authorization头中解析token获取用户ID
        authorization = request.headers.get("authorization")
        if authorization:
            try:
                # Bearer token格式: "Bearer <token>"
                scheme, token = authorization.split(" ", 1) if " " in authorization else (None, authorization)
                if scheme and scheme.lower() == "bearer":
                    payload = decode_access_token(token)
                    if payload and "sub" in payload:
                        user_id = payload.get("sub")
                        if user_id:
                            return f"user:{user_id}"
            except Exception:
                # token解析失败，继续使用IP
                pass
        
        # 使用IP地址
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _cleanup_expired(self):
        """清理过期的访问记录"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - self.window_seconds
        identifiers_to_remove = []
        
        for identifier, timestamps in self.requests.items():
            # 只保留时间窗口内的记录
            self.requests[identifier] = [
                ts for ts in timestamps if ts > cutoff_time
            ]
            # 如果该标识符没有有效记录了，标记为删除
            if not self.requests[identifier]:
                identifiers_to_remove.append(identifier)
        
        # 删除没有记录的标识符
        for identifier in identifiers_to_remove:
            del self.requests[identifier]
        
        self.last_cleanup = current_time
    
    def _is_rate_limited(self, identifier: str) -> Tuple[bool, int]:
        """
        检查是否超过限流
        返回: (是否限流, 剩余请求数)
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # 获取该标识符的访问记录
        timestamps = self.requests[identifier]
        
        # 清理过期记录
        valid_timestamps = [ts for ts in timestamps if ts > cutoff_time]
        self.requests[identifier] = valid_timestamps
        
        # 检查是否超过限制
        if len(valid_timestamps) >= self.max_requests:
            return True, 0
        
        # 记录本次访问
        valid_timestamps.append(current_time)
        self.requests[identifier] = valid_timestamps
        
        remaining = self.max_requests - len(valid_timestamps)
        return False, remaining
    
    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和根路径
        if request.url.path in ["/health", "/api/health", "/"]:
            return await call_next(request)
        
        # 定期清理过期记录
        self._cleanup_expired()
        
        # 获取请求标识符
        identifier = self._get_identifier(request)
        
        # 检查限流
        is_limited, remaining = self._is_rate_limited(identifier)
        
        if is_limited:
            # 返回429 Too Many Requests
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "data": None,
                    "message": f"请求过于频繁，请稍后再试"
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_seconds),
                    "Retry-After": str(self.window_seconds)
                }
            )
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流响应头
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window_seconds)
        
        return response
