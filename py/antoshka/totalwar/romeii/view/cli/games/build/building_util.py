import typing as ty
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from antoshka.totalwar.romeii.fixed.model.campaign_name import CAMPAIGN_CODE_TO_NAME
from antoshka.totalwar.romeii.view.cli.games.util import get_selected_game
from antoshka.totalwar.romeii.fixed.db import list_faction_technologies
from antoshka.totalwar.romeii.regionsopt.fixed.building_api import list_buildings as opt_api__list_buildings, Building


def list_buildings_by_research_points(max_research_points: int = 800) -> ty.Dict[str, Building]:
    game = get_selected_game()

    faction_tech = list_faction_technologies(game.faction_code,  CAMPAIGN_CODE_TO_NAME[game.campaign_code])

    buildings = opt_api__list_buildings(game.faction_code)
    buildings = {fb.name: fb for fb in buildings}

    b_technology = list(fixed_db.BuildingTechnology
                        .select()
                        .join(fixed_db.Technology)
                        .where(fixed_db.BuildingTechnology.building.in_(list(buildings)),
                               fixed_db.BuildingTechnology.technology.in_(faction_tech)))
    b_technology = {b_.building.code_name: b_.technology.research_points for b_ in b_technology}

    print(b_technology)

    for b_name, research_points in b_technology.items():
        if research_points >= max_research_points:
            print('pop', b_name)
            buildings.pop(b_name, None)

    return buildings