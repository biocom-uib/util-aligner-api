from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData


_base_metadata = MetaData(
    naming_convention={
        "pk": "%(table_name)s_pk",
        "fk": "%(table_name)s_%(column_0_name)s_foreign",
        "ck": "%(table_name)s_%(constraint_name)s",
        "ix": '%(table_name)s_%(column_0_name)s_index',
        "uq": "%(table_name)s_%(column_0_name)s_unique",
    }
)
Base = declarative_base(metadata=_base_metadata)
