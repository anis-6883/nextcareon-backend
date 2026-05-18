
import pytest
from sqlmodel import Session, select


# ---------------------------------------------------------------------------
# DB smoke tests
# ---------------------------------------------------------------------------
def test_db_session_yields(session):
    """Session fixture creates a valid SQLModel Session."""
    assert isinstance(session, Session)


def test_db_can_execute(session):
    """Session can execute raw SQL against the test DB."""
    from sqlalchemy import text
    result = session.exec(select(text("1"))).all()  # type: ignore
    assert result is not None


# ---------------------------------------------------------------------------
# Redis smoke tests
# ---------------------------------------------------------------------------
def test_redis_set_and_get(fake_redis):
    fake_redis.set("test_key", "hello")
    assert fake_redis.get("test_key") == "hello"


def test_redis_expiry(fake_redis):
    fake_redis.setex("expiring_key", 1, "value")
    assert fake_redis.get("expiring_key") == "value"


def test_redis_delete(fake_redis):
    fake_redis.set("del_key", "to_delete")
    fake_redis.delete("del_key")
    assert fake_redis.get("del_key") is None


# ---------------------------------------------------------------------------
# RedisCache helper tests
# ---------------------------------------------------------------------------
def test_redis_cache_set_get(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    cache.set("my_key", {"name": "Career_AI", "version": 1})
    result = cache.get("my_key")
    assert result == {"name": "Career_AI", "version": 1}


def test_redis_cache_ttl(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    cache.set("ttl_key", "expires", ttl=3600)
    ttl = fake_redis.ttl("test:ttl_key")
    assert 0 < ttl <= 3600


def test_redis_cache_delete(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    cache.set("gone_key", "data")
    cache.delete("gone_key")
    assert cache.get("gone_key") is None


def test_redis_cache_missing_key_returns_none(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    assert cache.get("nonexistent_key") is None


def test_redis_cache_set_membership(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    cache.set_add("blacklist", "token_abc123")
    assert cache.set_is_member("blacklist", "token_abc123") is True
    assert cache.set_is_member("blacklist", "token_xyz") is False


def test_redis_cache_increment(fake_redis):
    from app.db.redis_client import RedisCache
    cache = RedisCache(fake_redis, prefix="test")
    result1 = cache.increment("counter")
    result2 = cache.increment("counter")
    result3 = cache.increment("counter", amount=5)
    assert result1 == 1
    assert result2 == 2
    assert result3 == 7


# ---------------------------------------------------------------------------
# CacheKeys helper tests
# ---------------------------------------------------------------------------
def test_cache_keys_roadmap():
    from app.db.redis_client import CacheKeys
    key = CacheKeys.roadmap("Engineering", "CSE", "web_developer")
    assert key == "roadmap:Engineering:CSE:web_developer"


def test_cache_keys_user_stats():
    from app.db.redis_client import CacheKeys
    key = CacheKeys.user_stats("user-uuid-123")
    assert key == "user_stats:user-uuid-123"


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------
def test_health_endpoint(client):
    """The /health endpoint returns a valid response."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "postgresql" in data["services"]
    assert "redis" in data["services"]


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Career_AI" in response.json()["message"]