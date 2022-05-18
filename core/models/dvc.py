from typing import TypedDict

from playhouse.sqlite_ext import IntegerField

from . import BaseModel


class DvcModel(BaseModel):
    """dvc channel model"""

    # channel
    channel_id = IntegerField(null=True, unique=True)


class DvcType(TypedDict):
    """dvc channel type"""
    channel_id: str


def initialize() -> DvcModel:
    DvcModel.create_table(True)
    return DvcModel
