from typing import Dict, List

from .base_model import BaseModel, DATABASE

# Models
from .member import DevMemberType, DevMember
from .dvc import DvcType, Dvc


def getModels() -> Dict[str, BaseModel]:
    modelsList: List[BaseModel] = [
        DevMember,
        Dvc,
    ]

    modelsDict: Dict[str, BaseModel] = dict()

    for modelClass in modelsList:
        modelsDict[modelClass.__name__] = modelClass

    return modelsDict
