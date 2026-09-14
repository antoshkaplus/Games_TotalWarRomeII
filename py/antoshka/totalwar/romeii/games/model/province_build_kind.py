from antoshka.totalwar.romeii.common import StrEnum, auto


class ProvinceBuildKind(StrEnum):
    """
    Foundation is a base build for a province.
    All other `ProvinceBuildKind` must have origin `Foundation` build.

    Primary build is a current final target build.
    It must be only one for province.

    If build is not Primary but still is of interest we can
    make it Secondary.

    To avoid deleting data and avoid clutter no longer of interest
    builds should be made Archived.
    """
    Foundation = auto()
    Primary = auto()
    Secondary = auto()
    Archived = auto()
