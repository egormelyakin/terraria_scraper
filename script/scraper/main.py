import os
import asyncio
import aiohttp
import json

from scrapers.itemscraper import ItemScraper
from scrapers.recipescraper import RecipeScraper
from scrapers.dropscraper import DropScraper
from scrapers.npcscraper import NpcScraper


def parse_cookies(cookies: str) -> dict:
    cookies_dict = {}
    for cookie in cookies.split(';'):
        cookie_str = cookie.strip()
        eq_index = cookie_str.index('=')
        key = cookie_str[:eq_index].strip()
        value = cookie_str[eq_index + 1:].strip()
        cookies_dict[key] = value
    return cookies_dict


def get_from_data(data: list[dict], field: str, value: str) -> list[dict]:
    return list(filter(lambda x: x[field] == value, data))


def download_images(url_names: list[tuple[str, str]], folder: str):
    os.makedirs(folder, exist_ok=True)
    loop = asyncio.get_event_loop()
    tasks = [download_image(url, folder, filename) for url, filename in url_names]
    loop.run_until_complete(asyncio.wait(tasks))


async def download_image(url: str, folder: str, filename: str):
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)


def main():
    cache_folder = "src/cache/"
    data_folder = "src/data/"
    image_folder = "src/images/"
    url = "https://terraria.fandom.com/wiki/Special:CargoQuery"
    with open('script/scraper/cookie.txt', 'r') as f:
        cookies = parse_cookies(f.read())

    item_scraper = ItemScraper(url, cookies, data_folder, cache_folder)
    recipe_scraper = RecipeScraper(url, cookies, data_folder, cache_folder)
    drop_scraper = DropScraper(url, cookies, data_folder, cache_folder)
    npc_scraper = NpcScraper(url, cookies, data_folder, cache_folder)

    item_data = item_scraper.get_parsed_data()
    recipe_data = recipe_scraper.get_parsed_data()
    drop_data = drop_scraper.get_parsed_data()
    npc_data = npc_scraper.get_parsed_data()

    item_image = []
    item_image_equipped = []
    item_image_placed = []
    npc_image = []

    for item in item_data:
        name = item['item_name']
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        name = name.replace(' ', '_')
        name = name.lower()
        if item['item_image']:
            url = item['item_image']
            filename = f'{name}.png'
            item_image.append((url, filename))
        if item['item_image_equipped']:
            url = item['item_image_equipped']
            filename = f'{name}_equipped.png'
            item_image_equipped.append((url, filename))
        if item['item_image_placed']:
            url = item['item_image_placed']
            filename = f'{name}_placed.png'
            item_image_placed.append((url, filename))

    for npc in npc_data:
        name = npc['npc_name']
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        name = name.replace(' ', '_')
        name = name.lower()
        if npc['npc_image']:
            url = npc['npc_image']
            filename = f'{name}.png'
            npc_image.append((url, filename))

    download_images(item_image, os.path.join(image_folder, 'item'))
    download_images(item_image_equipped, os.path.join(image_folder, 'item_equipped'))
    download_images(item_image_placed, os.path.join(image_folder, 'item_placed'))
    download_images(npc_image, os.path.join(image_folder, 'npc'))

    tables = set()
    for recipe in recipe_data:
        for station in recipe['recipe_station']:
            tables.add(station)
    tables = list(tables)
    table_data = []
    table_name_replacements = {
        "Chair": "Wooden Chair",
        "Table": "Wooden Table",
        "Placed Bottle": "Bottle",
    }
    non_item_tables = {
        "Demon Altar": "https://static.wikia.nocookie.net/terraria_gamepedia/images/f/f8/Demon_Altar.png",
        "Honey": "https://static.wikia.nocookie.net/terraria_gamepedia/images/c/c6/Honey.png",
        "Lava": "https://static.wikia.nocookie.net/terraria_gamepedia/images/2/27/Lava.png",
        "Snow Biome": "https://static.wikia.nocookie.net/terraria_gamepedia/images/f/fa/Snow_Block.png",
        "Water": "https://static.wikia.nocookie.net/terraria_gamepedia/images/9/9d/Water.png"
    }
    for table in tables:
        replaced_name = table_name_replacements.get(table, table)
        if (table_item := get_from_data(item_data, 'item_name', replaced_name)):
            table_item = table_item[0]
            if table_item['item_image_placed']:
                table_image = table_item['item_image_placed']
            elif table_item['item_image']:
                table_image = table_item['item_image']
            else:
                table_image = None
        elif (table_image := non_item_tables.get(table)):
            pass
        else:
            table_image = None
        table_data.append({
            'table_name': table,
            'table_image': table_image
        })
    table_image = []
    for table in table_data:
        name = table['table_name']
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        name = name.replace(' ', '_')
        name = name.lower()
        if table['table_image']:
            url = table['table_image']
            filename = f'{name}.png'
            table_image.append((url, filename))
    download_images(table_image, os.path.join(image_folder, 'table'))
    with open(os.path.join(data_folder, 'Tables.json'), 'w') as f:
        f.write(json.dumps(table_data, indent=4))

    with open('script/scraper/src/boss.json', 'r') as f:
        boss_data = json.loads(f.read())
    with open('script/scraper/src/event.json', 'r') as f:
        event_data = json.loads(f.read())

    boss_image = []
    for boss in boss_data:
        name = boss['boss_name']
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        name = name.replace(' ', '_')
        name = name.lower()
        if boss['boss_icon']:
            url = boss['boss_icon']
            filename = f'{name}.png'
            boss_image.append((url, filename))
    download_images(boss_image, os.path.join(image_folder, 'boss'))

    with open(os.path.join(data_folder, 'Bosses.json'), 'w') as f:
        f.write(json.dumps(boss_data, indent=4))
    with open(os.path.join(data_folder, 'Events.json'), 'w') as f:
        f.write(json.dumps(event_data, indent=4))

    drop_scraper.print_field_layouts("rate")
if __name__ == '__main__':
    main()
