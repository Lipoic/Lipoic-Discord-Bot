from typing import Dict, List, Optional, TypedDict

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel


class MemberApply(BaseModel):
    """Member Apply model"""

    # thread_id
    thread_id = IntegerField(null=False, unique=True)
    # email
    email = TextField(null=False)
    # check code
    code = TextField(null=True)
    # jobs string list
    apply_status = JSONField(default=lambda: {})
    # apply stage
    apply_stage = IntegerField(null=False)


class MemberApplyType(TypedDict):
    """Member Apply type"""
    # thread_id
    thread_id: int
    # email
    email: str
    # check code
    code: Optional[str]
    # jobs string list
    apply_status: Dict[str, bool]
    # apply stage
    apply_stage: int
