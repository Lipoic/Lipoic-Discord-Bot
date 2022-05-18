from typing import Dict, List

from .base_model import BaseModel, DATABASE

# Models
from .member import DevMemberType, DevMemberModel, initialize as initializeDevMemberModel
from .dvc import DvcType, DvcModel, initialize as initializeDvcModel


def initializeModels():
    DATABASE.connect()

    # init models
    modelsDict: Dict[str, BaseModel] = {}
    modelsList: List[BaseModel] = [
        initializeDevMemberModel(),
        initializeDvcModel(),
    ]
    for modelClass in modelsList:
        modelsDict[modelClass.__name__] = modelClass

    DATABASE.close()

    return modelsDict
