import typing as ty
import peewee
from antoshka.totalwar.romeii.save.model import db as save_db
from antoshka.totalwar.romeii.fixed.model import db as fixed_db
from collections import defaultdict


fixed_db_path = '/home/antoshkaplus/Documents/Games_TotalWarRomeII/data_lfs/fixed.db'
db_path = '/home/antoshkaplus/Documents/Games_TotalWarRomeII/tmp/my_auto_save_legendary/my_auto_save_legendary.db'
faction_code_name = 'rom_getae'


fixed_db.DB.init(fixed_db_path)
save_db.DB.init(db_path)


province_name = {item.province_code_name: item.province_name for item in fixed_db.ProvinceScreen.select()}
settlement_name = {item.region_code_name: item.settlement_name for item in fixed_db.RegionScreen.select()}

my_faction = save_db.Faction.get(save_db.Faction.code_name == faction_code_name)
my_regions = my_faction.regions
my_regions: ty.Iterable[save_db.Region]


my_province_regions = defaultdict(list)
for my in my_regions:
    my_province_regions[my.province.code_name].append(my)


# now show buildings.


for province_code_name, regions in my_province_regions.items():
    print(province_name[province_code_name])
    for my in regions:
        print('  ', my.province_capital, settlement_name[my.code_name])


for province_code_name, regions in my_province_regions.items():
    print(province_code_name)
    for my in regions:
        print('  ', my.province_capital, my.code_name)


res = save_db.Region.select(save_db.Region.province,
                            peewee.fn.COUNT(save_db.Region.code_name).alias('count')).group_by(save_db.Region.province).execute()
print(res)
for rr in res:
    print(type(rr.province), rr.province, rr.count)