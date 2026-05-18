from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Import ALL models here so their tables appear in SQLModel.metadata.
# Every time you add a new model file, add its import here.

from app.models.user import User  # 
from app.models.career_path import CareerPath  # 
from app.models.skill import Skill  # 
from app.models.project import Project  # 
from app.models.resource import Resource  #
from app.models.milestone import Milestone  # 

from app.core.config import settings


# Alembic Config object (reads alembic.ini)

alembic_cfg = context.config

# so we never hard-code credentials in alembic.ini
alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up logging as configured in alembic.ini
if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name)

# Use SQLModel metadata as the migration target
target_metadata = SQLModel.metadata



# Offline mode (run migrations without a live DB connection)

def run_migrations_offline() -> None:
    url = alembic_cfg.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render column-level CHECK constraints from Python Enum types
        render_as_batch=False,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# Online mode (connect to DB and apply migrations directly)
def run_migrations_online() -> None:
    connectable = engine_from_config(
        alembic_cfg.get_section(alembic_cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No pooling inside the migration runner
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,       # Detect column type changes
            compare_server_default=True,  # Detect default value changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()