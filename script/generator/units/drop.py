from dataclasses import dataclass
from enum import StrEnum

from info_list import InfoList


class DropSourceType(StrEnum):
    NPC = "NPC"
    CHEST = "Chest"


@dataclass
class DropInfo:
    value_normal: tuple[float, float] = None
    value_expert: tuple[float, float] = None
    value_master: tuple[float, float] = None


@dataclass
class Drop:
    drop_source: str = None
    drop_source_type: DropSourceType = None
    drop_item: str = None
    drop_amount: DropInfo | None = None
    drop_chance: DropInfo | None = None

    def init_from_data(self, data: dict):
        self.drop_source = data["drop_source"]
        source_type = data["drop_source_type"].lower()
        for source_type_enum in DropSourceType:
            if source_type_enum.value.lower() == source_type:
                self.drop_source_type = source_type_enum
        self.drop_item = data["drop_item"]
        if data["drop_amount"]:
            self.drop_amount = DropInfo(
                data["drop_amount"][0],
                data["drop_amount"][1],
                data["drop_amount"][2]
            )
        else:
            self.drop_amount = None
        if data["drop_rate"]:
            self.drop_chance = DropInfo(
                data["drop_rate"][0],
                data["drop_rate"][1],
                data["drop_rate"][2]
            )
        else:
            self.drop_chance = None

    def __str__(self):
        string = f'(DROP) {self.drop_source} ({self.drop_source_type})'
        if self.drop_amount:
            string += f' {self.drop_amount.value_normal[0]}-{self.drop_amount.value_normal[1]}'
        if self.drop_chance:
            min_chance, max_chance = self.drop_chance.value_normal
            if min_chance == max_chance:
                string += f' {min_chance}%'
            else:
                string += f' {min_chance}-{max_chance}%'
        string += f' {self.drop_item}'
        return string


class Drops(InfoList):
    def __init__(self, content: list[dict]):
        drops = []
        for drop_data in content:
            drop = Drop()
            drop.init_from_data(drop_data)
            drops.append(drop)
        super().__init__(drops, "drop_item")
