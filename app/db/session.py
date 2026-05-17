from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings



connect_args: dict= {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False #set to True locally to see SQL in the terminal

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True, # test each connection before use (drops stale ones)
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args=connect_args,
)

# Session Dependency

def get_session() -> Generator[Session,None,None]:
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            Session.rollback()
            raise   

    SessionDep = Annotated[Session,Depends(get_session)] 


# Table createion

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables() -> None:
    SQLModel.metadata.drop_all(engine)