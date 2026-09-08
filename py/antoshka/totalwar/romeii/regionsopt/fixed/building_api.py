import typing as ty
from collections import defaultdict
from antoshka.totalwar.romeii.fixed.db.faction_buildings import list_faction_buildings
from antoshka.totalwar.romeii.fixed.model import db
from antoshka.totalwar.romeii.fixed.model.building_superchain import BuildingSuperchain
import effect_map
from .building import Building


def list_buildings(faction_code_name: str) -> ty.List[Building]:
    code_names = list_faction_buildings(faction_code_name)

    buildings = {item.code_name: item for item in db.Building.select().where(db.Building.code_name.in_(code_names))}

    building_effects = defaultdict(dict)
    for item in db.BuildingEffect.select().where(db.BuildingEffect.code_name.in_(code_names)):
        pair = (item.effect_name, item.scope)
        if pair in effect_map.province_stats:
            my_effect_name = effect_map.province_stats[pair]
            building_effects[item.code_name][my_effect_name] = item.value
        if pair in effect_map.faction_stats:
            my_effect_name = effect_map.faction_stats[pair]
            building_effects[item.code_name][my_effect_name] = item.value

    # since need to assign parents, map `TO` -> `FROM`
    building_upgrade = { item.to_code_name: item.from_code_name
                         for item in db.BuildingUpgrade.select().where(
                            db.BuildingUpgrade.to_code_name.in_(code_names))}

    res = []
    for name in code_names:
        bb = Building(name, building_upgrade.get(name), building_effects.get(name, {}),
                      buildings[name].resource_requirement,
                      BuildingSuperchain.parse(buildings[name].superchain))
        res.append(bb)

    return res