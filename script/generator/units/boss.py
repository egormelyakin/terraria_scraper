from dataclasses import dataclass
from enum import StrEnum

from info_list import InfoList


class SummonSourceType(StrEnum):
    ITEM = "Item"
    OBJECT = "Object"
    NPC = "NPC"
    ITEM_AND_OBJECT = "Item and Object"
    ENEMY = "Enemy"
    AUTO = "Auto"
    EVENT = "Event"


@dataclass
class Boss:
    boss_name: str = None
    boss_image: str = None
    boss_summon_source_type: SummonSourceType = None
    boss_summon_source: list[str] = None
    boss_summon_count: int = None
    boss_prerequisite: list[str] = None

    def init_from_data(self, data: dict):
        self.boss_name = data["boss_name"]
        self.boss_image = data["boss_icon"]
        summon_source_type = data["boss_summon_type"].lower()
        for summon_source_type_enum in SummonSourceType:
            if summon_source_type_enum.value.lower() == summon_source_type:
                self.boss_summon_source_type = summon_source_type_enum
        self.boss_summon_source = data["boss_summon"]
        self.boss_summon_count = data["boss_summon_count"]
        self.boss_prerequisite = data["boss_prerequisite"]

    def __str__(self):
        string = f'(BOSS) {self.boss_name}'
        string += f' ({self.boss_summon_source_type})'
        string += f' {self.boss_summon_source}'
        string += f' {self.boss_summon_count}'
        string += f' ({", ".join(self.boss_prerequisite)})'
        return string


class Bosses(InfoList):
    def __init__(self, content: list[dict]):
        bosses = []
        for boss_data in content:
            boss = Boss()
            boss.init_from_data(boss_data)
            bosses.append(boss)
        super().__init__(bosses, "boss_name")
