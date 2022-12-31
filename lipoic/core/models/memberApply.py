from typing import Optional, TypedDict, TYPE_CHECKING

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel

if TYPE_CHECKING:
    from core.types.MemberApply import jobsType, EventData


class MemberApply(BaseModel):
    """Member Apply model"""

    # thread ID
    thread_id = IntegerField(null=False, unique=True)
    # message ID
    message_id = IntegerField(null=False, unique=True)
    # job verify code
    code = TextField(null=True)
    # job that has been passed
    pass_job = TextField(null=True)
    # data
    data = JSONField(default=lambda: {})


class MemberApplyType(TypedDict):
    """Member Apply type"""

    # thread ID
    thread_id: int
    # message ID
    message_id: int
    # email
    email: str
    # job verify code
    code: Optional[str]
    # job that has been passed
    pass_job: Optional["jobsType"]
    # data
    data: "EventData"
