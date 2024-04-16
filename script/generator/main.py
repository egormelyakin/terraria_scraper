import json
import os
import time

from units.item import Item, Items
from units.recipe import Recipe, Recipes
from units.drop import Drop, Drops
from units.npc import NPC, NPCs
from units.boss import Boss, Bosses
from units.table import Table, Tables
from units.event import Event, Events
from nodes.item_node import ItemNode, generate_tree, step_by_step

import dataclasses


def load_json(path: str) -> list[dict] | dict:
    with open(path, 'r') as f:
        return json.load(f)


def print_info(info: Item | Recipe | Drop | NPC | Boss | Table | Event):
    print(json.dumps(dataclasses.asdict(info), indent=4))


def sanitize_name(name: str):
    name_sanitized = ''
    for char in name:
        if char.isalnum() or char == ' ':
            name_sanitized += char
    name_sanitized = name_sanitized.lower()
    name_sanitized = name_sanitized.replace(' ', '_')
    return name_sanitized


def main():
    data_path = 'src/data'

    data_files = [
        (Items, "items_parsed.json", "items"),
        (Drops, "drops_parsed.json", "drops"),
        (Recipes, "recipes_parsed.json", "recipes"),
        (NPCs, "npcs_parsed.json", "npcs"),
        (Bosses, "bosses.json", "bosses"),
        (Tables, "tables.json", "tables"),
        (Events, "events.json", "events")
    ]

    data = {}
    for data_class, data_file, data_name in data_files:
        data[data_name] = data_class(load_json(os.path.join(data_path, data_file)))
    data['misc'] = load_json('script/generator/src/misc.json')
    data['objects'] = load_json('script/generator/src/objects.json')

    with open('script/generator/items.txt', 'r') as f:
        items = f.read().splitlines()

    missing_images = set()
    missing_videos = set()
    generated = set([
        "Work Bench",
        "Furnace",
        "Iron Anvil",
        "Mythril Anvil",
        "Adamantite Forge"
    ])
    info = []

    for item in items:
        tree = generate_tree(item, data, generated)
        tree.print_tree()
        prev_missing_images = missing_images.copy()
        prev_missing_videos = missing_videos.copy()
        to_clean = [tree]
        guide = step_by_step(tree)
        guide_formatted = {}
        guide_formatted['item'] = item
        guide_formatted['image'] = f'images/item/{sanitize_name(item)}.png'
        guide_formatted['video'] = f'videos/show_{sanitize_name(item)}.mp4'
        if not os.path.isfile(f'src/{guide_formatted["video"]}'):
            missing_videos.add(guide_formatted["video"])
        guide_formatted['guide'] = []
        for step in guide:
            step_formatted = {}
            step_formatted['item'] = step['item']
            step_formatted['image'] = step['image']
            step_formatted['options'] = []
            for note in step['options']:
                note_formatted = {}
                note_formatted['video'] = note.video
                note_formatted['type'] = note.type
                if not os.path.isfile(f'src/{note.video}'):
                    missing_videos.add(note.video)
                note_formatted['content'] = []
                for content in note.content:
                    note_formatted['content'].append(dataclasses.asdict(content))
                    if not os.path.isfile(f'src/{content.note_image}'):
                        missing_images.add(content.note_image)
                step_formatted['options'].append(note_formatted)
            guide_formatted['guide'].append(step_formatted)
        info.append(guide_formatted)
        new_missing_images = missing_images - prev_missing_images
        new_missing_videos = missing_videos - prev_missing_videos
        for video in new_missing_videos:
            print(f'New missing video: {video}')
        print()
        # generated.add(item)

    missing_videos = list(missing_videos)
    missing_videos.sort()
    for video in missing_videos:
        print(f'Missing video: {video}')

    with open('guide.json', 'w') as f:
        json.dump(info, f, indent=4)

    # missing_images = list(missing_images)
    # for image in missing_images:
    #     print(image)
    # print(f'{len(missing_images)} missing images')

    # missing_videos = list(missing_videos)
    # missing_videos.sort()
    # for video in missing_videos:
    #     print(video)
    # print(f'{len(missing_videos)} missing videos')


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f'({(end - start)*1000: .0f}ms)')
