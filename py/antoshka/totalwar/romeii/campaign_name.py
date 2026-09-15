from antoshka.totalwar.romeii.common import StrEnum, auto


class CampaignName(StrEnum):
    Grand = auto()


CAMPAIGN_NAME_TO_CODE = {
    CampaignName.Grand: 'main_rome'
}