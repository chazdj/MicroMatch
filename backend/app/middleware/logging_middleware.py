from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import SystemLog
from ..core.auth import decode_access_token


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = None
        role = None

        # Try to extract user info from JWT without blocking the request
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("user_id")
                role = payload.get("role")

        response = await call_next(request)

        # Write log entry
        db: Session = SessionLocal()
        try:
            log = SystemLog(
                user_id=user_id,
                role=role,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        return response
