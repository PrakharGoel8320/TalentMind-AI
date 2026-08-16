import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse

class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.clients = defaultdict(list)
        
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        self.clients[client_ip] = [req for req in self.clients[client_ip] if req > now - self.window]
        
        if len(self.clients[client_ip]) >= self.requests:
            return False
            
        self.clients[client_ip].append(now)
        return True

limiter = RateLimiter(requests=100, window=60)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else '127.0.0.1'
        if not limiter.is_allowed(client_ip):
            return JSONResponse(status_code=429, content={'detail': 'Too Many Requests'})
        return await call_next(request)
