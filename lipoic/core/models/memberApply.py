from typing import Optional, TypedDict, TYPE_CHECKING

from playhouse.sqlite_ext import IntegerField, TextField, JSONField

from . import BaseModel

if TYPE_CHECKING:
    from core.types.MemberApply import jobType, EventData


class MemberApply(BaseModel):
    """Member Apply model"""

    # thread ID
    thread_id = IntegerField(null=False, unique=True)
    # apply message ID
    message_id = IntegerField(null=False, unique=True)
    # meeting channel ID
    meeting_channel_id = IntegerField(null=True, unique=True)
    # meeting message ID
    meeting_message_id = IntegerField(null=True, unique=True)
    # meeting timestamp
    meeting_time = IntegerField(null=True)
    # meeting member ID
    meeting_member = IntegerField(null=True)
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
    # apply message ID
    message_id: int
    # meeting channel ID
    channel_id: int
    # meeting message ID
    meeting_message_id: int
    # meeting timestamp
    meeting_time: int
    # meeting member ID
    meeting_member: int
    # email
    email: str
    # job verify code
    code: Optional[str]
    # job that has been passed
    pass_job: Optional["jobType"]
    # data
    data: "EventData"
