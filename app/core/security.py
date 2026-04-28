from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import forbidden_error, unauthorized_error
from app.database.session import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(data: dict[str, Any]) -> str:
    if "sub" not in data or "role" not in data:
        raise ValueError("Access token data must include 'sub' and 'role'.")

    token_data = data.copy()
    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    token_data.update({"exp": expires_at})

    return jwt.encode(
        token_data,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise unauthorized_error() from exc

    return payload


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if user_id is None:
        raise unauthorized_error()

    try:
        user_id_int = int(user_id)
    except ValueError as exc:
        raise unauthorized_error() from exc

    user = db.get(User, user_id_int)

    if user is None or not user.is_active:
        raise unauthorized_error()

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise forbidden_error()

    return current_user
