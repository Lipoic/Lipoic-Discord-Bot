from typing import List, TypedDict

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel


class MemberApply(BaseModel):
    """Member Apply model"""

    # user id
    user_id = IntegerField(null=True, unique=True)
    # check code
    code = TextField(null=True)
    # jobs string list
    job = JSONField(default=lambda: [])


class MemberApplyType(TypedDict):
    """Member Apply type"""
    user_id: int
    code: str
    job: List[str]
