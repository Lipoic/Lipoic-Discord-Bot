from typing import Optional, TypedDict, List
from playhouse.sqlite_ext import IntegerField, TextField, JSONField


from . import BaseModel


class DevMemberModel(BaseModel):
    """dev members data model"""

    # dev member dc id
    user_id = IntegerField(null=True, unique=True)

    # dev member name
    name = TextField(null=True)

    # dev member position list
    position = JSONField(default=lambda: [])

    # dev member github name
    github_name = TextField(unique=True)


class DevMemberType(TypedDict):
    """Dev Member data Type"""
    user_id: int
    name: Optional[str]
    position: List[str]
    github_name: Optional[str]
