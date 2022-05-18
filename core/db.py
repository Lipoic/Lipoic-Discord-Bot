from ast import Dict

from .models import DATABASE, initializeModels

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import LIPOIC
    from .models import BaseModel, DevMemberModel, DvcModel


class DB:
    DevMemberModel: 'DevMemberModel'
    DvcModel: 'DvcModel'

    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot
        self.database = DATABASE
        self._models: Dict[str, 'BaseModel'] = dict()

        self.loadModels()

    def connect(self):
        self.database.connect()
        return self

    def loadModels(self):
        self._models = models = initializeModels()
        for [name, model] in dict.items(models):
            setattr(self, name, model)
