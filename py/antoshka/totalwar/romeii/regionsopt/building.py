import typing as ty
from typing import Protocol


type Name = str


class Building(Protocol):
    # Primary building is a head building of region.
    @property
    def primary(self) -> bool:
        # False - `secondary` or `secondary_port`
        pass

    @property
    def secondary_port(self) -> bool:
        pass

    # Both major and minor properties are required,
    # since one building could be placed in either slot.
    @property
    def major(self) -> bool:
        pass

    @property
    def minor(self) -> bool:
        pass

    @property
    def name(self) -> Name:
        pass

    @property
    def parent_name(self) -> Name:
        pass

    @property
    def need_resource(self) -> ty.Optional[str]:
        pass