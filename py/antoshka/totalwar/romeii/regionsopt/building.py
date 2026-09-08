import typing as ty
from typing import Protocol


type Name = str


class Building(Protocol):
    @property
    def name(self) -> Name:
        pass

    @property
    def parent_name(self) -> Name:
        pass

    @property
    def need_resource(self) -> ty.Optional[str]:
        pass

    @property
    def stats(self) -> ty.Dict[str, int|float]:
        pass

    @property
    def port(self) -> bool:
        pass

    @property
    def major_primary(self) -> bool:
        pass

    @property
    def minor_primary(self) -> bool:
        pass

    @property
    def major_secondary(self) -> bool:
        pass

    @property
    def minor_secondary(self) -> bool:
        pass