from enum import StrEnum, auto


class BuildingSuperchain(StrEnum):
    Agriculture = auto() # minor
    AgricultureBarb = auto() # major
    CityCenter = auto() # major
    MilitaryBuff = auto() # major
    MilitaryMain = auto() # both
    MilitarySecondary = auto() # both
    Mine = auto() # minor
    Port = auto() # special
    Resource = auto() # minor primary
    SanitationBarb = auto() # minor
    SettlementMajor = auto() # major primary
    SettlementMinor = auto() # minor primary
    Temple = auto()

    @property
    def port(self) -> bool:
        return self == BuildingSuperchain.Port

    @property
    def major_primary(self) -> bool:
        return self == BuildingSuperchain.SettlementMajor

    @property
    def minor_primary(self) -> bool:
        return self == BuildingSuperchain.SettlementMinor or self == BuildingSuperchain.Resource

    # Both major and minor properties are required,
    # since one building could be placed in either slot.
    @property
    def major_secondary(self) -> bool:
        return self in [BuildingSuperchain.AgricultureBarb, BuildingSuperchain.CityCenter, BuildingSuperchain.MilitaryBuff,
                        BuildingSuperchain.MilitaryMain, BuildingSuperchain.MilitarySecondary, BuildingSuperchain.Temple]

    @property
    def minor_secondary(self) -> bool:
        return self in [BuildingSuperchain.Agriculture, BuildingSuperchain.MilitaryMain, BuildingSuperchain.MilitarySecondary,
                        BuildingSuperchain.Mine, BuildingSuperchain.SanitationBarb, BuildingSuperchain.Temple]
