from typing import List, TypedDict

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel


class MemberApply(BaseModel):
    """Member Apply model"""

    # channel
    user_id = IntegerField(null=True, unique=True)
    # user id
    code = TextField(null=True)
    job = JSONField(default=lambda: [])


class MemberApplyType(TypedDict):
    """Member Apply type"""
    user_id: str
    code: str
    job: List[str]
