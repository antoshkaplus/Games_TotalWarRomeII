import types
import typing as ty
from enum import StrEnum as _StrEnum, auto


Ctx = types.SimpleNamespace
T = ty.TypeVar('T')


class StrEnum(_StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


def partition(pred: ty.Callable[[T], bool], iterable: ty.Iterable[T]) -> ty.Tuple[ty.List[T], ty.List[T]]:
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses