from dataclasses import dataclass

from info_list import InfoList


@dataclass
class Table:
    table_name: str = None
    table_image: str = None

    def init_from_data(self, data: dict):
        self.table_name = data["table_name"]
        self.table_image = data["table_image"]

    def __str__(self):
        string = f'(TABLE) {self.table_name}'
        return string


class Tables(InfoList):
    def __init__(self, content: list[dict]):
        tables = []
        for table_data in content:
            table = Table()
            table.init_from_data(table_data)
            tables.append(table)
        super().__init__(tables, "table_name")
