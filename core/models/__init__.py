from typing import Dict, List

from .base_model import BaseModel, DATABASE

# Models
from .member import DevMemberType, DevMemberModel
from .dvc import DvcType, DvcModel


def getModels() -> Dict[str, BaseModel]:
    modelsList: List[BaseModel] = [
        DevMemberModel,
        DvcModel,
    ]

    modelsDict: Dict[str, BaseModel] = dict()

    for modelClass in modelsList:
        modelsDict[modelClass.__name__] = modelClass

    return modelsDict
