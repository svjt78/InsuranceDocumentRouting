import os
import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool

# ─── 1. Add your backend folder to sys.path so "import app.database" works ───
#    This file is in <project_root>/alembic/env.py, so go up two levels:
project_dir = Path(__file__).resolve().parent.parent
backend_dir = project_dir / "backend"
sys.path.insert(0, str(backend_dir))

# ─── 2. Load .env from the project root ───────────────────────────────────────
load_dotenv(project_dir / ".env")

# ─── 3. Alembic config and logging setup ────────────────────────────────────
config = context.config
# override the SQLALCHEMY URL with the one from .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))

if config.config_file_name:
    fileConfig(config.config_file_name)

# ─── 4. Import your metadata for `--autogenerate` ────────────────────────────
import app.models  # noqa: F401  ensure all models are registered
from app.database import Base
target_metadata = Base.metadata

# ─── 5. Offline migrations ───────────────────────────────────────────────────
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ─── 6. Online migrations ────────────────────────────────────────────────────
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

# ─── 7. Entrypoint ───────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
