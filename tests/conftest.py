from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_usd_to_brl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.vehicle_service.get_usd_to_brl", lambda: 5.0)


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        role="ADMIN",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def regular_user(db_session: Session) -> User:
    user = User(
        email="user@example.com",
        password_hash=hash_password("user123"),
        role="USER",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token({"sub": str(admin_user.id), "role": admin_user.role})


@pytest.fixture
def user_token(regular_user: User) -> str:
    return create_access_token({"sub": str(regular_user.id), "role": regular_user.role})
