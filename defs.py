from enum import Enum

class divisions(Enum):
    one = 'I'
    two = 'II'
    three = 'III'
    four = 'IV'


class tier_major(Enum):
    challenger = 'https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?'
    grandmaster = 'https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?'
    master ='https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?'
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class tier_minor(Enum):
    diamond = 'DIAMOND'
    emerald = 'EMERALD'
    gold = 'GOLD'
    silver = 'SILVER'
    bronze = 'BRONZE'
    iron = 'IRON'
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_