from dataclasses import dataclass

from info_list import InfoList


@dataclass
class NPC:
    npc_name: str = None
    npc_image: str = None
    npc_hardmode: bool = None
    npc_environment: list[str] = None

    def init_from_data(self, data: dict):
        self.npc_name = data["npc_name"]
        self.npc_image = data["npc_image"]
        self.npc_hardmode = data["npc_hardmode"]
        self.npc_environment = data["npc_environment"]

    def __str__(self):
        string = f'(NPC) {self.npc_name}'
        string += f' ({", ".join(self.npc_environment)})'
        return string


class NPCs(InfoList):
    def __init__(self, content: list[dict]):
        npcs = []
        for npc_data in content:
            npc = NPC()
            npc.init_from_data(npc_data)
            npcs.append(npc)
        super().__init__(npcs, "npc_name")
