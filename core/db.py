
from .models import DATABASE, getModels

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from . import LIPOIC
    from .models import BaseModel, DevMemberModel, DvcModel


class DB:
    DevMember: 'DevMemberModel'
    Dvc: 'DvcModel'

    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot
        self.database = DATABASE
        self._models: Dict[str, 'BaseModel'] = getModels()

        self.create_tables()

    def connect(self):
        self.database.connect()
        return self

    def create_tables(self):
        with self.database:
            self.database.create_tables(dict.values(self._models))
