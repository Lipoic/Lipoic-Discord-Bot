from typing import TypedDict
from playhouse.sqlite_ext import IntegerField


from . import BaseModel


class Member(BaseModel):
    """member data model"""
    user_id = IntegerField(null=True, unique=True)
    chef_count = IntegerField(default=0)


class MemberType(TypedDict):
    """member data model Type"""
    user_id: int
    chef_count: int
