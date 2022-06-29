from typing import Any, Generic, TypeVar


T = TypeVar("T")

__all__ = ["ShallowData", "MISSING"]


class _MissingSentinel:
    def __eq__(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return "..."

    def __repr__(self) -> str:
        return self.__str__()


MISSING: Any = _MissingSentinel()


class ShallowData(Generic[T]):
    def __init__(self, data: T) -> None:
        self._data = data

    def __call__(self, set_data: T = MISSING) -> T:
        if set_data is not MISSING:
            self._data = set_data
        return self._data

    def __eq__(self, value: Any) -> bool:
        return self._data == value

    def __ne__(self, value: Any) -> bool:
        return not self.__eq__(value)

    @property
    def data(self) -> T:
        return self()

    @data.setter
    def data(self, data: T) -> None:
        self(data)
