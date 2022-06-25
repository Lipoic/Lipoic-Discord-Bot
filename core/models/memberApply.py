from typing import Dict, List, Optional, TypedDict

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel


class MemberApply(BaseModel):
    """Member Apply model"""

    # thread ID
    thread_id = IntegerField(null=False, unique=True)
    # email
    email = TextField(null=False)
    # job verify code
    code = TextField(null=True)
    # job that has been passed
    pass_job = TextField(null=True)


class MemberApplyType(TypedDict):
    """Member Apply type"""
    # thread ID
    thread_id: int
    # email
    email: str
    # job verify code
    code: Optional[str]
    # job that has been passed
    pass_job: Optional[str]
