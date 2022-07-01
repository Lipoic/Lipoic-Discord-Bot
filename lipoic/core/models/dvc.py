from typing import TypedDict

from playhouse.sqlite_ext import IntegerField

from . import BaseModel


class Dvc(BaseModel):
    """dvc channel model"""

    # channel
    channel_id = IntegerField(null=True, unique=True)
    # user id
    user_id = IntegerField(null=True)


class DvcType(TypedDict):
    """dvc channel type"""

    channel_id: str
