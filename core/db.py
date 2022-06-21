import peewee
import random
from string import ascii_letters, digits
from .models import DATABASE, getModels

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from . import LIPOIC
    from .models import BaseModel, DevMember, Dvc, Member, MemberApply


class DB:
    DevMember: 'DevMember'
    Dvc: 'Dvc'
    Member: 'Member'
    MemberApply: 'MemberApply'

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

    def create_apply_member_check_code(self, id: str):
        applyDB = self.MemberApply

        def create_code():
            return ''.join(random.sample(ascii_letters + digits, k=6))
        try:
            code_str = create_code()
            applyDB.get(
                applyDB.thread_id == id
            ).update(code=code_str).execute()
        except peewee.IntegrityError:
            return self.create_apply_member_check_code()
        return code_str
