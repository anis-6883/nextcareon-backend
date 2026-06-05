"""app/db/base.py - SQLModel base class with common configuration."""

from sqlmodel import SQLModel

class Base(SQLModel, table=False):
    """Base model with common SQLModel configuration."""

    pass