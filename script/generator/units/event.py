from dataclasses import dataclass
from enum import StrEnum

from info_list import InfoList


@dataclass
class EventEnemyGroup:
    enemy_group_prereq: list[str] = None
    enemy_group_enemies: list[str] = None


class EventSummonType(StrEnum):
    NATURAL = "Natural"
    OBJECT = "Object"
    ITEM_AND_OBJECT = "Item and Object"
    ITEM = "Item"
    ENEMY = "Enemy"


@dataclass
class Event:
    event_name: str = None
    event_summon_type: EventSummonType = None
    event_summon_item: list[str] = None
    event_enemies: list[EventEnemyGroup] = None
    event_prerequesite: list[str] = None

    def init_from_data(self, data: dict):
        self.event_name = data["event_name"]
        summon_type = data["event_summon_type"].lower()
        for summon_type_enum in EventSummonType:
            if summon_type_enum.value.lower() == summon_type:
                self.event_summon_type = summon_type_enum
        self.event_summon_item = data["event_summon_item"]
        self.event_enemies = []
        for enemy_group in data["event_enemies"]:
            enemy_group_obj = EventEnemyGroup()
            enemy_group_obj.enemy_group_prereq = enemy_group["event_enemies_prerequisite"]
            enemy_group_obj.enemy_group_enemies = enemy_group["event_enemies_list"]
            self.event_enemies.append(enemy_group_obj)
        self.event_prerequesite = data["event_prerequisite"]

    def __str__(self):
        string = f'(EVENT) {self.event_name}'
        string += f' ({self.event_summon_type})'
        string += f' {", ".join(self.event_summon_item)}'
        string += f' ({", ".join(self.event_prerequesite)})'
        return string


class Events(InfoList):
    def __init__(self, content: list[dict]):
        events = []
        for event_data in content:
            event = Event()
            event.init_from_data(event_data)
            events.append(event)
        super().__init__(events, "event_name")
