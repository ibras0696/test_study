import asyncio
import re
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from core.db import Base
import core.models  # noqa: F401  # Import side effects register ORM tables in Base.metadata

target_metadata = Base.metadata
VERSIONS_DIR = Path(__file__).resolve().parent / "versions"
REVISION_PREFIX_RE = re.compile(r"^(?P<prefix>\d{4})_")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _next_revision_id() -> str:
    """Return the next numeric revision prefix from existing migration files."""

    highest = 0
    for migration_file in VERSIONS_DIR.glob("*.py"):
        match = REVISION_PREFIX_RE.match(migration_file.name)
        if match:
            highest = max(highest, int(match.group("prefix")))
    return f"{highest + 1:04d}"


def _assign_numeric_revision_id(context, revision, directives) -> None:
    """Set a sequential revision id for newly generated migrations."""

    cmd_opts = getattr(context.config, "cmd_opts", None)
    if getattr(cmd_opts, "rev_id", None):
        return

    if directives:
        directives[0].rev_id = _next_revision_id()


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        process_revision_directives=_assign_numeric_revision_id,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations through a sync connection wrapper."""

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,  # нужно для SQLite
        process_revision_directives=_assign_numeric_revision_id,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations."""

    configuration = config.get_section(config.config_ini_section)

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connection = config.attributes.get("connection")

    if connection is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
