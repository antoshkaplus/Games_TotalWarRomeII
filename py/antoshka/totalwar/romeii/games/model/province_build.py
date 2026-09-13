from __future__ import annotations
import typing as ty
from antoshka.totalwar.romeii.common.serializable import Serializable


type ProvinceCode = str
type RegionCode = str
type BuildingCode = str
type RegionsBuild = ty.Dict[RegionCode, ty.List[BuildingCode]]


class ProvinceBuild(Serializable):
    def __init__(self, province_code: ProvinceCode, regions_build: RegionsBuild):
        self.province_code = province_code
        self.regions_build = regions_build

    def to_serializable(self):
        return { 'province_code': self.province_code,
                 'regions_build': self.regions_build }

    @staticmethod
    def from_serializable(obj) -> ProvinceBuild:
        return ProvinceBuild(obj['province_code'], obj['regions_build'])