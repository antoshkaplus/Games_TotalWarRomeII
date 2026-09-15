


cli commands:
* create game : source file name
    or maybe for testing use "faction_code" and "campaign_code" (Grand is default (rom_main))
* 
* list games:
    should show: faction, campaign code, create ts, last selected, last updated and so on.
* 
* select game.
    this is the game we will apply following commands.
    Once selected we can know selected game by `last selected` field in game table.
    This operation will be performed rarely, that is why we do not want to specify this field every single time.
* 
* update: 
    from source file. 
        we should check that game id is matching.
        then we parse from calling c++ process and then 
        we loaded in python and pick up / update 
        provinces.
    manually add new regions/provinces. Better go region by region.
        Must provide existing buildings when doing it.

* list provinces (names + regions. suffix regions with + if mine and - if not mine)
* optimize - provide province name. and optimization parameters
    all optimization results will be kept in a separate table. 
    Ones that are interesting user can mark Primary, Secondary.
    + when it was done. Primary mark can be only one. 
    But previous Primary is still going to be around if we sort Secondary in Timestamp 
    order.

    Mark:
        Unmarked
        Primary 
        Secondary

* list provinces_primary build
    for each province list Primary build.

* list_province_builds
* get_province_build
    here we are interested in build details, not just buildings. 
    maybe add flags to ask for more details.

# read config

# latest game should be considered current

# create new game -> provide save file.
# will call c++ program to parse and make json from the save file.
# then from json data we take game related



province ownership
 Province Region

From Province Ownership can figure out what regions to build???





standard_solver()
    regions, port_regions, min_food, min_order,
    no_resources=False, no_major=False, prune_sz=2000, research=False, depth=None


    I'm insterested in passing FactionStats. 
    
    Can store global_stats in init_candidates solutions.
    Also should include any existing bonuses for this particular region.
