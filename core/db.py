
from .models import DATABASE, getModels

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from . import LIPOIC
    from .models import BaseModel, DevMember, Dvc


class DB:
    DevMember: 'DevMember'
    Dvc: 'Dvc'

    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot
        self.database = DATABASE
        self._models: Dict[str, 'BaseModel'] = getModels()

        self.load_models()
        self.create_tables()

    def connect(self):
        self.database.connect()
        return self

    def create_tables(self):
        self.database.connect()

        with self.database:
            self.database.create_tables(dict.values(self._models))

        self.database.close()

    def load_models(self):
        for model in dict.values(self._models):
            setattr(self, model.__name__, model)
