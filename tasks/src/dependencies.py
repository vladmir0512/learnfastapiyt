from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError

SECRET_KEY = "super_secret"
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False))):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"email": payload.get("sub"), "user_id": payload.get("user_id")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def context_dependency(current_user: str = Depends(get_current_user)):
    return {"current_user": current_user}