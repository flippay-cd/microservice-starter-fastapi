import asyncio
import datetime
import importlib
import pathlib
import sys
from logging.config import fileConfig
from typing import Any, cast

from alembic import context
from alembic.operations.ops import MigrationScript
from alembic.runtime.migration import MigrationContext
from exp_async_db.database import Database
from exp_async_db.models import Base
from sqlalchemy import Connection, pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1] / "app"
sys.path.append(str(PROJECT_DIR))

from core.config import settings  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", settings.POSTGRES_DSN)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def load_models() -> None:
    """Dynamically load models from installed apps."""
    for app in settings.INSTALLED_APPS:
        try:
            importlib.import_module(f"{app}.models")
        except ImportError as e:
            print(f"Could not import models from {app}: {e}")  # noqa: T201


# Load all models from installed apps
load_models()

target_metadata = Base.metadata
schema = settings.POSTGRES_SCHEMA

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")  # noqa: ERA001
# ... etc.


def do_run_migrations(connection: Connection) -> None:
    def process_revision_directives(
        _context: MigrationContext, _revision: tuple[str, str], directives: list[MigrationScript]
    ) -> None:
        rev_id = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d")
        for directive in directives:
            directive.rev_id = rev_id

        assert config.cmd_opts is not None
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            assert script.upgrade_ops is not None
            if script.upgrade_ops.is_empty():
                directives[:] = []

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,  # type: ignore[arg-type]
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        cast("dict[str, Any]", config.get_section(config.config_ini_section)),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=Database._default_connect_args,
    )

    async with connectable.connect() as connection:
        # set search path on the connection, which ensures that
        # PostgreSQL will emit all CREATE / ALTER / DROP statements
        # in terms of this schema by default
        await connection.execute(text(f'create schema if not exists "{schema}"'))
        await connection.execute(text(f'set search_path to "{schema}"'))
        # in SQLAlchemy v2+ the search path change needs to be committed
        await connection.commit()

        connection.dialect.default_schema_name = schema

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
