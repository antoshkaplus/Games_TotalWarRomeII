from __future__ import annotations
from antoshka.totalwar.romeii.common import StrEnum, auto


class BuildingSuperchain(StrEnum):
    Agriculture = auto() # minor
    AgricultureBarb = auto() # major
    CityCentre = auto() # major
    MilitaryBuff = auto() # major
    MilitaryMain = auto() # both
    MilitarySecondary = auto() # both
    Mine = auto() # minor
    Port = auto() # special

    ResourceAmber = auto() # minor primary
    ResourceDye = auto()
    ResourceGlass = auto()
    ResourceGold = auto()
    ResourceGrain = auto()
    ResourceHorse = auto()
    ResourceIron = auto()
    ResourceLead = auto()
    ResourceLeather = auto()
    ResourceLumber = auto()
    ResourceMarble = auto()
    ResourceOlive = auto()
    ResourceSalt  = auto()
    ResourceSilk = auto()
    ResourceSpice = auto()
    ResourceWine = auto()

    SanitationBarb = auto() # minor
    SettlementMajor = auto() # major primary
    SettlementMinor = auto() # minor primary
    Temple = auto()

    @property
    def port_kind(self) -> bool:
        return self == BuildingSuperchain.Port

    @property
    def resource_kind(self) -> bool:
        return self.value.startswith('Resource')

    @property
    def major_primary(self) -> bool:
        return self == BuildingSuperchain.SettlementMajor

    @property
    def minor_primary(self) -> bool:
        return self == BuildingSuperchain.SettlementMinor or self.resource_kind

    # Both major and minor properties are required,
    # since one building could be placed in either slot.
    @property
    def major_secondary(self) -> bool:
        return self in [BuildingSuperchain.AgricultureBarb, BuildingSuperchain.CityCentre, BuildingSuperchain.MilitaryBuff,
                        BuildingSuperchain.MilitaryMain, BuildingSuperchain.MilitarySecondary, BuildingSuperchain.Temple]

    @property
    def minor_secondary(self) -> bool:
        return self in [BuildingSuperchain.Agriculture, BuildingSuperchain.MilitaryMain, BuildingSuperchain.MilitarySecondary,
                        BuildingSuperchain.Mine, BuildingSuperchain.SanitationBarb, BuildingSuperchain.Temple]

    @staticmethod
    def parse(superchain: str) -> BuildingSuperchain:
        return BuildingSuperchain(superchain)