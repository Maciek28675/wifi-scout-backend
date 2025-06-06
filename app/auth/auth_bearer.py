from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth_handler import decode_jwt
from app.db import get_db
from sqlalchemy.orm import Session
from app.models import User

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        payload = decode_jwt(token)
        return payload is not None

async def get_current_user(token: str = Depends(JWTBearer())) -> User:
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(status_code=403, detail="Invalid or expired token.")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid token payload.")

    db: Session = next(get_db())
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user
