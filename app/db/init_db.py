import logging

from sqlmodel import SQLModel

# Import every model so SQLModel.metadata knows about all tables.
# If you add a new model file, add the import here too.
from app.models.career_path import CareerPath  # noqa: F401
from app.models.milestone import Milestone  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.resource import Resource  # noqa: F401
from app.models.skill import Skill  # noqa: F401
from app.models.user import User  # noqa: F401

from app.db.session import engine

logger = logging.getLogger(__name__)


def create_db_and_tables() -> None:
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully.")


def drop_db_and_tables() -> None:
    logger.warning("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    logger.warning("All database tables dropped.")