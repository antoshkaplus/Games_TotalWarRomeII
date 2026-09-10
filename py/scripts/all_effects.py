import argparse
from collections import defaultdict
from antoshka.totalwar.romeii.fixed.model import db as fixed_db


db_path = "/home/antoshkaplus/Documents/Games_TotalWarRomeII/data_lfs/fixed.db"
fixed_db.DB.init(db_path)


building_effects = defaultdict(list)
for be in fixed_db.BuildingEffect.select(fixed_db.BuildingEffect.effect_name,
                                         fixed_db.BuildingEffect.scope).distinct():
    print(be.effect_name, be.scope)



