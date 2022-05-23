from typing import Dict, List

from .base_model import BaseModel, DATABASE

# Models
from .devMember import DevMemberType, DevMember
from .member import Member, MemberType
from .dvc import DvcType, Dvc


def getModels() -> Dict[str, BaseModel]:
    modelsList: List[BaseModel] = [
        DevMember,
        Member,
        Dvc,
    ]

    modelsDict: Dict[str, BaseModel] = dict()

    for modelClass in modelsList:
        modelsDict[modelClass.__name__] = modelClass

    return modelsDict
