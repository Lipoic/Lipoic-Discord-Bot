import pathlib

from playhouse.sqlite_ext import SqliteDatabase, Model

pathlib.Path("data").mkdir(parents=True, exist_ok=True)

DATABASE = SqliteDatabase(
    "data/data.db",
    pragmas={
        "journal_mode": "wal",
        "cache_size": -1 * 64000,  # 64MB
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    },
)


class BaseModel(Model):
    class Meta:
        database = DATABASE
