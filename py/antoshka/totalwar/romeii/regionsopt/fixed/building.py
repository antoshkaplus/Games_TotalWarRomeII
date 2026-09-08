import typing as ty
from antoshka.totalwar.romeii.fixed.model.building_superchain import BuildingSuperchain
from antoshka.totalwar.romeii.regionsopt.building import Building as BuildingProtocol, Name


class Building(BuildingProtocol):
    def __init__(self, name: str, parent_name: ty.Optional[str],
                 stats: ty.Dict[str, int|float], need_resource: ty.Optional[str],
                 superchain: BuildingSuperchain):
        self._name = name
        self._parent_name = parent_name
        self._need_resource = need_resource
        self._stats = stats
        self.superchain = superchain

    @property
    def name(self) -> Name:
        return self._name

    @property
    def parent_name(self) -> Name:
        return self._parent_name

    @property
    def need_resource(self) -> ty.Optional[str]:
        return self._need_resource

    @property
    def stats(self) -> ty.Dict[str, int|float]:
        return self._stats

    @property
    def port(self) -> bool:
        return self.superchain.port

    @property
    def major_primary(self) -> bool:
        return self.superchain.major_primary

    @property
    def minor_primary(self) -> bool:
        return self.superchain.minor_primary

    @property
    def major_secondary(self) -> bool:
        return self.superchain.major_secondary

    @property
    def minor_secondary(self) -> bool:
        return self.superchain.minor_secondary
