from pathlib import Path
from .base import *

__all__ = (
    "__version__",
    "__base_dir__",
    "__config_path__",
)


__version__ = "0.0.1"
__base_dir__ = Path(__file__).resolve().parent
__config_path__ = __base_dir__.parent
