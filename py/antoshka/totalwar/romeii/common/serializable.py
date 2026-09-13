from __future__ import annotations
from abc import ABC, abstractmethod


class Serializable(ABC):
    """
    Serializable python object, by definition,
    is python object made from json natually
    supported type variables.

    Custom type is called Serializable if it
    can be converted to Serializable python object and
    from Serializable python object, implements interface
    below.
    """

    @abstractmethod
    def to_serializable(self):
        ...

    @staticmethod
    @abstractmethod
    def from_serializable(obj) -> Serializable:
        ...


class Serializable_B(ABC):
    """
    Certain classes could not be self-contained, meaning
    they require an external dependency to function properly.
    That makes it problematic to make an instance out of
    serialized data. We could remember to set external dependencies
    after calling `@staticmethod def from_serializable(obj) -> Serializable:`,
    but that is error-prone, relies on a human too much.
    In this class we require to create an instance with external dependencies set first.
    After that user can call `@abstractmethod def from_serializable(self, obj):`
    to set fields from serialized data.
    """

    @abstractmethod
    def to_serializable(self):
        ...

    @abstractmethod
    def from_serializable(self, obj):
        ...
