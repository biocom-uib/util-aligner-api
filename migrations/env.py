from __future__ import with_statement
from alembic import context
from sqlalchemy import pool
from sqlalchemy.enginge import create_engine
from logging.config import fileConfig

from api.model import Base
from config import config as api_config
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# Take the tables list from the declared model
metadata_tables = list(target_metadata.tables.keys())


# This will tell alembic to ignore tables that are not defined in metadata.
def include_object(object, name, type_, reflected, compare_to):
    if ((type_ == "table" and name not in metadata_tables) or object.info.get("skip_autogenerate", False)):
        return False
    else:
        return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = api_config['DATABASE_DSN']
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, include_object=include_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(api_config['DATABASE_DSN'], poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


context.include_object = include_object


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
