from typing import List, Optional, TypedDict

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel


class MemberApply(BaseModel):
    """Member Apply model"""

    # thread_id
    thread_id = IntegerField(null=True, unique=True)
    # email
    email = TextField(null=True)
    # check code
    code = TextField()
    # jobs string list
    job = JSONField(default=lambda: [])
    # TODO add annotation
    apply_job = JSONField(default=lambda: [])


class MemberApplyType(TypedDict):
    """Member Apply type"""
    # thread_id
    thread_id: int
    # email
    email: str
    # check code
    code: Optional[str]
    # jobs string list
    job: List[str]
    apply_job: List[str]
