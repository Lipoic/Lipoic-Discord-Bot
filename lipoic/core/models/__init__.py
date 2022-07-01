from typing import Dict, List


from .base_model import BaseModel, DATABASE

# Models
from .devMember import DevMember, DevMemberType
from .member import Member, MemberType
from .dvc import Dvc, DvcType
from .memberApply import MemberApply, MemberApplyType

__all__ = [
    "BaseModel",
    "DATABASE",
    "DevMember",
    "DevMemberType",
    "Member",
    "MemberType",
    "Dvc",
    "DvcType",
    "MemberApply",
    "MemberApplyType",
]


def getModels() -> Dict[str, BaseModel]:
    modelsList: List[BaseModel] = [
        DevMember,
        Member,
        Dvc,
        MemberApply,
    ]

    modelsDict: Dict[str, BaseModel] = dict()

    for modelClass in modelsList:
        modelsDict[modelClass.__name__] = modelClass

    return modelsDict
