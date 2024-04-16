from dataclasses import dataclass, field
from enum import StrEnum


class NoteType(StrEnum):
    TEXT = "Text"
    IMAGE = "Image"


@dataclass
class NoteContent:
    note_type: NoteType
    note_text: str
    note_image: str = None
    note_count: int = 1


class TextNote:
    def __init__(self, item_node, group):
        self.content = []
        self.video = None
        if group.group_type == GroupType.RECIPE:
            self.init_from_recipe(item_node, group)
            self.type = 'Recipe'
        elif group.group_type == GroupType.DROP:
            self.init_from_drop(item_node, group)
            self.type = 'Drop'
        elif group.group_type == GroupType.VENDOR:
            self.init_from_vendor(item_node, group)
            self.type = 'Vendor'
        # elif group.group_type == GroupType.EVENT:
        #     self.init_from_event(item_node, group)
        #     self.type = 'Event'
        elif group.group_type == GroupType.SUMMON:
            self.init_from_summon(item_node, group)
            self.type = 'Summon'
        elif group.group_type == GroupType.OBTAIN:
            self.init_from_obtain(item_node, group)
            self.type = 'Obtain'

    def __str__(self):
        result = []
        for content in self.content:
            if content.note_type == NoteType.TEXT:
                result.append(f"{content.note_text}")
            elif content.note_type == NoteType.IMAGE:
                result.append(f"[{content.note_count} {content.note_text}]")
        return "".join(result)

    def node_note(self, node):
        if node.node_type == NodeType.ITEM:
            image = self.image_path(node.content[0].title, "item")
        elif node.node_type == NodeType.TABLE:
            image = self.image_path(node.content[0].title, "table")
        elif node.node_type == NodeType.CHEST:
            image = self.image_path(node.content[0].title, "item")
        elif node.node_type == NodeType.NPC:
            image = self.image_path(node.content[0].title, "npc")
        elif node.node_type == NodeType.BOSS:
            image = self.image_path(node.content[0].title, "boss")
        elif node.node_type == NodeType.EVENT:
            image = None
        elif node.node_type == NodeType.OBJECT:
            image = self.image_path(node.content[0].title, "object")
        return NoteContent(
            note_type=NoteType.IMAGE,
            note_text=node.content[0].title,
            note_image=image,
            note_count=node.count
        )

    def node_list(self, node_list: list, additive: bool = False):
        content = []
        if len(node_list) == 1:
            content.append(self.node_note(node_list[0]))
        elif len(node_list) == 2:
            content.append(self.node_note(node_list[0]))
            content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" and " if additive else " or "
            ))
            content.append(self.node_note(node_list[1]))
        else:
            for i, node in enumerate(node_list):
                if i == len(node_list) - 1:
                    content.append(NoteContent(
                        note_type=NoteType.TEXT,
                        note_text="and " if additive else "or "
                    ))
                    content.append(self.node_note(node))
                else:
                    content.append(self.node_note(node))
        return content

    def sanitize_name(self, name: str):
        name_sanitized = ''
        for char in name:
            if char.isalnum() or char == ' ':
                name_sanitized += char
        name_sanitized = name_sanitized.lower()
        name_sanitized = name_sanitized.replace(' ', '_')
        return name_sanitized

    def image_path(self, item_name: str, folder: str):
        name_sanitized = self.sanitize_name(item_name)
        return f"images/{folder}/{name_sanitized}.png"


    def init_from_recipe(self, item_node, group):
        table_node = group.elements[0]
        ingredient_nodes = group.elements[1:]

        if len(ingredient_nodes) == 1:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text="Craft "
            ))
        else:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text="Combine "
            ))

        self.content.extend(self.node_list(ingredient_nodes, additive=True))

        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text=" into "
        ))
        self.content.append(self.node_note(item_node))
        if table_node.content[0].title == "By Hand":
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text="by hand"
            ))
        else:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" at "
            ))
            self.content.append(self.node_note(table_node))
        video = f'table_{self.sanitize_name(table_node.content[0].title)}'
        self.video = f'videos/{video}.mp4'

    def init_from_drop(self, item_node, group):
        drop_nodes = group.elements
        chest_nodes = [node for node in drop_nodes if node.node_type == NodeType.CHEST]
        enemy_nodes = [node for node in drop_nodes if node.node_type in [
            NodeType.NPC, NodeType.BOSS]]

        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text="Get "
        ))
        self.content.append(self.node_note(item_node))
        if chest_nodes and enemy_nodes:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" by looting "
            ))
            self.content.extend(self.node_list(chest_nodes))
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" or by killing "
            ))
            self.content.extend(self.node_list(enemy_nodes))
        elif chest_nodes:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" by looting "
            ))
            self.content.extend(self.node_list(chest_nodes))
        elif enemy_nodes:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" by killing "
            ))
            self.content.extend(self.node_list(enemy_nodes))
        video = f'drop_{self.sanitize_name(drop_nodes[0].content[0].title)}'
        self.video = f'videos/{video}.mp4'

    def init_from_vendor(self, item_node, group):
        vendor_nodes = group.elements

        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text="Buy "
        ))
        self.content.append(self.node_note(item_node))
        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text=" from "
        ))
        self.content.extend(self.node_list(vendor_nodes))
        video = f'vendor_{self.sanitize_name(vendor_nodes[0].content[0].title)}'
        self.video = f'videos/{video}.mp4'

    def init_from_event(self, item_node, group):
        event_nodes = group.elements

        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text="Find "
        ))
        self.content.append(self.node_note(item_node))
        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text=" during "
        ))
        self.content.extend(self.node_list(event_nodes))
        video = f'event_{self.sanitize_name(event_nodes[0].content[0].title)}'
        self.video = f'videos/{video}.mp4'

    def init_from_summon(self, item_node, group):
        summon_nodes = group.elements

        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text="Summon "
        ))
        self.content.append(self.node_note(item_node))

        if summon_nodes[0].node_type == NodeType.ITEM:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" using "
            ))
            self.content.extend(self.node_list(summon_nodes))
        elif len(summon_nodes)>1 and summon_nodes[0].node_type == NodeType.OBJECT and summon_nodes[1].node_type == NodeType.ITEM:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" at "
            ))
            self.content.extend(self.node_list(summon_nodes[:1]))
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" using "
            ))
            self.content.extend(self.node_list(summon_nodes[1:]))
        elif summon_nodes[0].node_type == NodeType.OBJECT:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" at "
            ))
            self.content.extend(self.node_list(summon_nodes))
        elif summon_nodes[0].node_type == NodeType.NPC:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" by killing "
            ))
            self.content.extend(self.node_list(summon_nodes, additive=True))
        elif summon_nodes[0].node_type == NodeType.BOSS:
            self.content.append(NoteContent(
                note_type=NoteType.TEXT,
                note_text=" by killing "
            ))
            self.content.extend(self.node_list(summon_nodes, additive=True))
        video = f'summon_{self.sanitize_name(item_node.content[0].title)}'
        self.video = f'videos/{video}.mp4'

    def init_from_obtain(self, item_node, group):
        self.content.append(NoteContent(
            note_type=NoteType.TEXT,
            note_text="Find and obtain "
        ))
        self.content.append(self.node_note(item_node))
        video = f'obtain_{self.sanitize_name(item_node.content[0].title)}'
        self.video = f'videos/{video}.mp4'


class NodeType(StrEnum):
    ITEM = "Item"
    TABLE = "Table"
    CHEST = "Chest"
    NPC = "NPC"
    BOSS = "Boss"
    EVENT = "Event"
    OBJECT = "Object"


class GroupType(StrEnum):
    RECIPE = "Recipe"
    DROP = "Drop"
    VENDOR = "Vendor"
    OTHER = "Other"
    EVENT = "Event"
    SUMMON = "Summon"
    OBTAIN = "Obtain"


@dataclass
class ChildGroup:
    group_type: GroupType
    elements: list = field(default_factory=list)
    note: TextNote = None

    def print_group(self, indent: list[str] = [], prefix: str = ''):
        line, fork, end, space = "│   ", "├── ", "└── ", "    "
        print(f"{''.join(indent[:-1])}{prefix}{self.group_type}")# ({self.note})")
        for i, element in enumerate(self.elements):
            if i == len(self.elements) - 1:
                child_indent = indent + [space]
                child_prefix = end
            else:
                child_indent = indent + [line]
                child_prefix = fork
            element.print_tree(child_indent, child_prefix)


@dataclass
class NodeContent:
    title: str
    image: str


@dataclass
class Node:
    content: list[NodeContent]
    node_type: NodeType
    count: int = 1
    children: list[ChildGroup] = field(default_factory=list)

    def print_tree(self, indent: list[str] = [], prefix: str = ''):
        line, fork, end, space = "│   ", "├── ", "└── ", "    "
        name = " + ".join([content.title for content in self.content])
        if self.count > 1:
            text = f"{name} ({self.count}) [{self.node_type}]"
        else:
            text = f"{name} [{self.node_type}]"
        print(f"{''.join(indent[:-1])}{prefix}{text}")
        if self.children:
            for i, child in enumerate(self.children):
                if i == len(self.children) - 1:
                    child_indent = indent + [space]
                    child_prefix = end
                else:
                    child_indent = indent + [line]
                    child_prefix = fork
                child.print_group(child_indent, child_prefix)
