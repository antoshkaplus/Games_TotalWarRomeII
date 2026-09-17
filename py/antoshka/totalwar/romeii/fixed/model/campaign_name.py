from antoshka.totalwar.romeii.common import StrEnum, auto


class CampaignName(StrEnum):
    Grand = auto()
    EmpireDivided = auto()
    ImperatorAugustus = auto()
    CaesarInGaul = auto()
    RiseOfTheRepublic = auto()
    WrathOfSparta = auto()
    HannibalAtTheGates = auto()


CAMPAIGN_NAME_TO_CODE = {
    CampaignName.Grand: 'main_rome',
    CampaignName.EmpireDivided: 'main_3c',
    CampaignName.ImperatorAugustus: 'main_emperor',
    CampaignName.CaesarInGaul: 'main_gaul',
    CampaignName.RiseOfTheRepublic: 'main_invasion',
    CampaignName.WrathOfSparta: 'main_greek',
    CampaignName.HannibalAtTheGates: 'main_punic',
}


def faction_code_campaign_name(faction_code: str) -> CampaignName:
    if faction_code.startswith('rom_'):
        return CampaignName.Grand
    if faction_code.startswith('3c_'):
        return CampaignName.EmpireDivided
    if faction_code.startswith('emp_'):
        return CampaignName.ImperatorAugustus
    if faction_code.startswith('gaul_'):
        return CampaignName.CaesarInGaul
    if faction_code.startswith('inv_'):
        return CampaignName.RiseOfTheRepublic
    if faction_code.startswith('pel_'):
        return CampaignName.WrathOfSparta
    if faction_code.startswith('pun_'):
        return CampaignName.HannibalAtTheGates

    raise RuntimeError()