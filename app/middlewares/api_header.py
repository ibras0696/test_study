from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AppHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # response.headers["TOKEN"] = "my-api"
        token = response.headers.get('TOKEN', '1')
        if request.url.path in ("/docs", '/openapi.json', '/redoc'):
            return response

        if token != "1234":
            return JSONResponse(
                status_code=403, 
                content={"detail": "Not Forbien"})
        return response
