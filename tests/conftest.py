
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from app.db.session import get_session
from app.db.redis_client import get_redis

# ---------------------------------------------------------------------------
# In-memory SQLite engine (isolated, fast, no Docker needed)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite://"  # In-memory


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


# ---------------------------------------------------------------------------
# Fake Redis (in-process, no real Redis needed)
# ---------------------------------------------------------------------------
@pytest.fixture(name="fake_redis")
def fake_redis_fixture():
    try:
        import fakeredis
        return fakeredis.FakeRedis(decode_responses=True)
    except ImportError:
        pytest.skip("fakeredis not installed — run: pip install fakeredis")


# ---------------------------------------------------------------------------
# TestClient with overridden dependencies
# ---------------------------------------------------------------------------
@pytest.fixture(name="client")
def client_fixture(session, fake_redis):
    def override_get_session():
        yield session

    def override_get_redis():
        yield fake_redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()