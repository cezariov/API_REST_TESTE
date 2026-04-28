from typing import Literal

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.errors import conflict_error, unauthorized_error
from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.repositories import user_repository
from app.schemas.auth import LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


class BootstrapUserRequest(BaseModel):
    email: str
    password: str
    role: Literal["USER", "ADMIN"] = "USER"


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = user_repository.get_by_email(db, data.email)

    if user is None or not user.is_active:
        raise unauthorized_error()

    if not verify_password(data.password, user.password_hash):
        raise unauthorized_error()

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/bootstrap", status_code=status.HTTP_201_CREATED)
def bootstrap_user(
    data: BootstrapUserRequest,
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    # Development/test helper only. Do not expose this endpoint in production.
    existing_user = user_repository.get_by_email(db, data.email)
    if existing_user:
        raise conflict_error("A user with this email already exists.")

    user = user_repository.create_user(
        db=db,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )

    return {"id": user.id, "email": user.email, "role": user.role}
