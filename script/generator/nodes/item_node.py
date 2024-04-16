import math
import os
import json
import dataclasses

from node import Node, NodeType, ChildGroup, NodeContent, GroupType, TextNote


class ItemNode(Node):
    def __init__(
        self,
        item_name: str,
        data: dict,
        count: int = 1,
        history: list[str] | None = None
    ):
        if item_name in data['misc']['name_replacements']:
            # print(f'Replacing "{item_name}" with "{data["misc"]["name_replacements"][item_name]}"')
            item_name = data['misc']['name_replacements'][item_name]
        item_data = data['items'].get_item('item_name', item_name)
        if item_data is None:
            raise ValueError(f'Item "{item_name}" not found')
        item_info = self.get_item_info(item_name, data)
        content = NodeContent(item_name, item_data.item_image)
        super().__init__([content], NodeType.ITEM, count)

        self.item_name = item_name
        self.count = count
        self.item_info = item_info
        self.data = data
        self.history = history or []

    def init_children(self):
        self.children = []
        if not self.children:
            self.init_obtain()
        if not self.children:
            self.init_recipes()
        if not self.children:
            self.init_drops()
        if not self.children:
            self.init_vendors()

    def get_item_info(self, item_name: str, data: dict):
        cache_file = f'src/info/{item_name}.json'
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        else:
            item_info = self.get_item_info_from_data(item_name, data)
            with open(cache_file, 'w') as f:
                json.dump(item_info, f, indent=4)
            return item_info

    def get_item_info_from_data(self, item_name: str, data: dict):
        item_info = {}

        recipes = []
        recipe_data = data['recipes'].get_items(
            'recipe_result_item', item_name
        )
        for recipe in recipe_data:
            recipes.append(dataclasses.asdict(recipe))
        item_info['recipes'] = recipes

        drops = []
        drop_data = data['drops'].get_items('drop_item', item_name)
        for drop in drop_data:
            drops.append(dataclasses.asdict(drop))
        item_info['drops'] = drops

        vendors = []
        item_data = data['items'].get_item('item_name', item_name)
        for vendor in item_data.item_vendors or []:
            vendor_info = {
                'vendor_name': vendor.value,
                'price': item_data.item_buy_price.amount,
                'currency': item_data.item_buy_price.currency.value,
            }
            vendors.append(vendor_info)
        item_info['vendors'] = vendors

        item_info['obtainable'] = False

        return item_info

    def init_recipes(self):
        recipes = self.item_info['recipes']
        if recipes:
            recipes = [recipes[0]]
        for recipe in recipes:
            recipe_group = ChildGroup(GroupType.RECIPE)
            craft_count = math.ceil(self.count / recipe['recipe_result_amount'])

            stations = recipe['recipe_station']
            station_content = []
            for station in stations:
                station_data = self.data['tables'].get_item('table_name', station)
                if station_data is None:
                    raise ValueError(f'Table "{station}" not found')
                station_image = station_data.table_image
                station_content.append(NodeContent(station, station_image))
            station_node = Node(station_content, NodeType.TABLE, 1)
            station_group = ChildGroup(GroupType.OTHER)
            for station in stations:
                if self.data['items'].get_item('item_name', station) is None:
                    continue
                station_item_node = ItemNode(
                    item_name=station,
                    data=self.data,
                    count=1,
                    history=self.history + [station]
                )
                station_group.elements.append(station_item_node)
            station_node.children.append(station_group)
            recipe_group.elements.append(station_node)

            for ingredient in recipe['recipe_ingredients']:
                if ingredient['item_name'] in self.history:
                    print(f'Loop detected: {self.history}')
                    continue
                ingredient_item_node = ItemNode(
                    item_name=ingredient['item_name'],
                    data=self.data,
                    count=ingredient['amount'] * craft_count,
                    history=self.history + [ingredient['item_name']]
                )
                recipe_group.elements.append(ingredient_item_node)
            self.children.append(recipe_group)

    def init_drops(self):
        drops = self.item_info['drops']

        drop_group = ChildGroup(GroupType.DROP)
        for drop in drops:
            if drop['drop_source_type'] == 'Chest':
                drop_group.elements.append(self.chest_node(
                    chest_name=drop['drop_source'],
                ))
            elif drop['drop_source_type'] == 'NPC':
                drop_group.elements.append(self.enemy_node(
                    enemy_name=drop['drop_source'],
                ))
            else:
                raise ValueError(f'Unknown drop source type: {drop["drop_source_type"]}')
        if drop_group.elements:
            self.children.append(drop_group)

    def chest_node(self, chest_name: str):
        chest_data = self.data['items'].get_item('item_name', chest_name)
        if chest_data is None:
            raise ValueError(f'Chest "{chest_name}" not found')
        chest_content = NodeContent(chest_name, chest_data.item_image)
        chest_node = Node([chest_content], NodeType.CHEST, 1)
        return chest_node

    def enemy_node(self, enemy_name: str):
        is_boss = False
        boss_data = None
        for boss in self.data['bosses']:
            if boss.boss_name == enemy_name:
                is_boss = True
                boss_data = boss
                break
        is_event = False
        event_data = None
        for event in self.data['events']:
            for enemy_group in event.event_enemies:
                if enemy_name in enemy_group.enemy_group_enemies:
                    is_event = True
                    event_data = event
                    break
        if is_boss and not is_event:
            return self.boss_node(boss_data=boss_data)
        elif not is_boss and not is_event:
            return self.npc_node(npc_name=enemy_name)
        elif is_event:
            return self.event_node(event_data=event_data, enemy_name=enemy_name)

    def boss_node(self, boss_data: dict):
        boss_node = self.npc_node(npc_name=boss_data.boss_name)
        summon_type = boss_data.boss_summon_source_type.value
        summon_source = boss_data.boss_summon_source

        summon_group = ChildGroup(GroupType.SUMMON)

        if summon_type == 'Item':
            summon_group.elements.append(ItemNode(
                item_name=summon_source[0],
                data=self.data,
                count=boss_data.boss_summon_count,
                history=self.history + [summon_source[0]]
            ))
        elif summon_type == 'Object':
            objects_data = self.data['objects']
            for entry in objects_data:
                if entry['object_name'] == summon_source[0]:
                    objects_data = entry
                    break
            else:
                raise ValueError(f'Object "{summon_source[0]}" not found')
            object_content = NodeContent(
                summon_source[0], objects_data['object_image']
            )
            summon_group.elements.append(Node([object_content], NodeType.OBJECT, 1))
        elif summon_type == 'Item and Object':
            objects_data = self.data['objects']
            for entry in objects_data:
                if entry['object_name'] == summon_source[1]:
                    objects_data = entry
                    break
            else:
                raise ValueError(f'Object "{summon_source[1]}" not found')
            object_content = NodeContent(
                summon_source[1], objects_data['object_image']
            )
            summon_node = Node([object_content], NodeType.OBJECT, 1)
            summon_node.children.append(ItemNode(
                item_name=summon_source[0],
                data=self.data,
                count=boss_data.boss_summon_count,
                history=self.history + [summon_source[0]]
            ))
            summon_group.elements.append(summon_node)
        elif summon_type == 'Enemy':
            for enemy_name in summon_source:
                summon_group.elements.append(self.enemy_node(enemy_name=enemy_name))
        elif summon_type == 'Auto':
            return boss_node
        else:
            raise ValueError(f'Unknown summon type: {summon_type}')
        boss_node.children.append(summon_group)


        return boss_node

    def npc_node(self, npc_name: str):
        boss_data = self.data['bosses'].get_item('boss_name', npc_name)
        if boss_data is not None:
            npc_content = NodeContent(npc_name, boss_data.boss_image)
            npc_node = Node([npc_content], NodeType.BOSS, 1)
            return npc_node
        else:
            if npc_name in self.data['misc']['npc_replacements']:
                print(f'Replacing "{npc_name}" with "{
                      self.data["misc"]["npc_replacements"][npc_name]}"')
                npc_name = self.data['misc']['npc_replacements'][npc_name]
            npc_data = self.data['npcs'].get_item('npc_name', npc_name)
            if npc_data is None:
                raise ValueError(f'NPC "{npc_name}" not found')
            npc_content = NodeContent(npc_name, npc_data.npc_image)
        npc_node = Node([npc_content], NodeType.NPC, 1)
        return npc_node

    def event_node(self, event_data: dict, enemy_name: str):
        enemy_node = self.npc_node(npc_name=enemy_name)
        event_content = NodeContent(event_data.event_name, None)
        event_node = Node([event_content], NodeType.EVENT, 1)

        summon_type = event_data.event_summon_type.value
        summon_source = event_data.event_summon_item
        
        summon_group = ChildGroup(GroupType.SUMMON)
        event_node.children.append(summon_group)

        if summon_type == 'Item':
            summon_node = ItemNode(
                item_name=summon_source[0],
                data=self.data,
                count=1,
                history=self.history + [summon_source[0]]
            )
            summon_group.elements.append(summon_node)
        elif summon_type == 'Object':
            objects_data = self.data['objects']
            for entry in objects_data:
                if entry['object_name'] == summon_source[0]:
                    objects_data = entry
                    break
            else:
                raise ValueError(f'Object "{summon_source[0]}" not found')
            object_content = NodeContent(
                summon_source[0], objects_data['object_image']
            )
            summon_node = Node([object_content], NodeType.OBJECT, 1)
            summon_group.elements.append(summon_node)
        elif summon_type == 'Item and Object':
            objects_data = self.data['objects']
            for entry in objects_data:
                if entry['object_name'] == summon_source[1]:
                    objects_data = entry
                    break
            else:
                raise ValueError(f'Object "{summon_source[1]}" not found')
            object_content = NodeContent(
                summon_source[1], objects_data['object_image']
            )
            object_node = Node([object_content], NodeType.OBJECT, 1)
            item_node = ItemNode(
                item_name=summon_source[0],
                data=self.data,
                count=1,
                history=self.history + [summon_source[0]]
            )
            summon_group.elements.append(object_node)
            summon_group.elements.append(item_node)
        elif summon_type == 'Enemy':
            summon_node = self.enemy_node(enemy_name=summon_source[0])
            summon_group.elements.append(summon_node)
        else:
            raise ValueError(f'Unknown summon type: {summon_type}')

        event_group = ChildGroup(GroupType.EVENT)
        event_group.elements.append(event_node)
        enemy_node.children.append(event_group)
        return enemy_node

    def average_drop_yield(self, drop: dict):
        average_amount = sum(drop['drop_amount']['value_normal']) / 2
        average_chance = sum(drop['drop_chance']['value_normal']) / 2
        return average_amount * average_chance

    def init_vendors(self):
        vendors = self.item_info['vendors']
        if not vendors:
            return
        vendor_group = ChildGroup(GroupType.VENDOR)
        for vendor in vendors:
            vendor_node = self.npc_node(npc_name=vendor['vendor_name'])
            vendor_group.elements.append(vendor_node)
        self.children.append(vendor_group)

    def init_obtain(self):
        obtainable = self.item_info['obtainable']
        if not obtainable:
            return
        obtain_group = ChildGroup(GroupType.OBTAIN)
        self.children.append(obtain_group)


def generate_tree(item_name: str, data: dict, generated_: set[str]):
    generated = generated_.copy()
    root = ItemNode(item_name, data)
    print(f'Generating tree for "{item_name}"')
    root.init_children()

    to_generate = []
    for child_group in root.children:
        child_group.note = TextNote(root, child_group)
        to_generate.extend(reversed(child_group.elements))
    while to_generate:
        element = to_generate.pop()
        if not isinstance(element, ItemNode):
            for child_group in reversed(element.children):
                child_group.note = TextNote(element, child_group)
                to_generate.extend(reversed(child_group.elements))
            continue
        if element.item_name in generated:
            continue
        generated.add(element.item_name)
        element.init_children()
        for child_group in reversed(element.children):
            child_group.note = TextNote(element, child_group)
            to_generate.extend(reversed(child_group.elements))

    to_clean = [root]
    while to_clean:
        node = to_clean.pop(0)
        cleaned = []
        for child_group in node.children:
            if child_group.group_type == GroupType.OTHER:
                if not child_group.elements:
                    continue
                if all(not child.children for child in child_group.elements):
                    continue
            cleaned.append(child_group)
        node.children = cleaned
        for child_group in node.children:
            to_clean.extend(child_group.elements)
    return root

def sanitize_name(name: str):
    name_sanitized = ''
    for char in name:
        if char.isalnum() or char == ' ':
            name_sanitized += char
    name_sanitized = name_sanitized.lower()
    name_sanitized = name_sanitized.replace(' ', '_')
    return name_sanitized

def step_by_step(root: Node):
    steps = []
    for child_group in root.children:
        for child in child_group.elements:
            steps.extend(step_by_step(child))
    options = {}
    options['item'] = root.content[0].title
    name = sanitize_name(options['item'])
    if root.node_type == NodeType.ITEM:
        options['image'] = f'images/item/{name}.png'
    elif root.node_type == NodeType.TABLE:
        options['image'] = f'images/table/{name}.png'
    elif root.node_type == NodeType.CHEST:
        options['image'] = f'images/item/{name}.png'
    elif root.node_type == NodeType.NPC:
        options['image'] = f'images/npc/{name}.png'
    elif root.node_type == NodeType.BOSS:
        options['image'] = f'images/boss/{name}.png'
    elif root.node_type == NodeType.EVENT:
        options['image'] = None
    elif root.node_type == NodeType.OBJECT:
        options['image'] = f'images/object/{name}.png'
    options['options'] = []
    for child_group in root.children:
        options['options'].append(child_group.note)
    if options['options'] and all(option.content for option in options['options']):
        steps.append(options)
    return steps
