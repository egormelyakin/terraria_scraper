from scraper import Scraper
from bs4 import BeautifulSoup as soup


class ItemScraper(Scraper):
    def __init__(
        self,
        url: str,
        cookies: dict = None,
        data_folder: str = None,
        cache_folder: str = None
    ):
        params = {}
        params['tables'] = 'Items'
        params['fields'] = ','.join([
            '_pageName=Page',
            '_pageTitle=PageTitle',
            '_pageNamespace=PageNamespace',
            '_pageID=PageID',
            '_ID=ID',
            'itemid=itemid',
            'name=name',
            'internalname=internalname',
            'image=image',
            'imagefile=imagefile',
            'imageplaced=imageplaced',
            'imageequipped=imageequipped',
            'autoswing=autoswing',
            'stack=stack',
            'consumable=consumable',
            'hardmode=hardmode',
            'type__full=type',
            'listcat__full=listcat',
            'tag__full=tag',
            'damage=damage',
            'damagetype=damagetype',
            'defense=defense',
            'velocity=velocity',
            'knockback=knockback',
            'research=research',
            'rare=rare',
            'buy=buy',
            'sell=sell',
            'axe=axe',
            'pick=pick',
            'hammer=hammer',
            'fishing=fishing',
            'bait=bait',
            'bonus=bonus',
            'toolspeed=toolspeed',
            'usetime=usetime',
            'unobtainable=unobtainable',
            'critical=critical',
            'tooltip=tooltip',
            'placeable=placeable',
            'placedwidth=placedwidth',
            'placedheight=placedheight',
            'mana=mana',
            'hheal=hheal',
            'mheal=mheal',
            'bodyslot=bodyslot',
            'buffs__full=buffs',
            'debuffs__full=debuffs'])
        super().__init__(url, params, cookies, data_folder, cache_folder)

    def get_data(self) -> list[dict]:
        data = super().get_data()
        return filter(self.__filter_item, data)

    def __filter_item(self, item: dict) -> bool:
        valid = True
        if item['name'] == 'Chain':
            return True
        valid &= item['itemid'] != ''
        valid &= item['internalname'] != 'None'
        return valid

    def parse(self) -> list[dict]:
        data = self.get_data()
        parsed = []
        for item in data:
            parsed.append(self.parse_item(item))
        return parsed

    def parse_item(self, item: dict) -> dict:
        parsed = {}
        # Page information
        parsed['page_url'] = self.__parse_page_url(item)
        parsed['page_title'] = self.__parse_page_title(item)
        parsed['page_id'] = self.__parse_page_id(item)
        # General information
        parsed['item_id'] = self.__parse_item_id(item)
        parsed['item_name'] = self.__parse_item_name(item)
        parsed['item_internal_name'] = self.__parse_item_internal_name(item)
        # Image information
        parsed['item_image'] = self.__parse_item_image(item)
        parsed['item_image_placed'] = self.__parse_item_image_placed(item)
        parsed['item_image_equipped'] = self.__parse_item_image_equipped(item)
        # Properties
        parsed['item_autoswing'] = self.__parse_item_autoswing(item)
        parsed['item_stack'] = self.__parse_item_stack(item)
        parsed['item_consumable'] = self.__parse_item_consumable(item)
        # Tags
        parsed['item_type'] = self.__parse_item_type(item)
        parsed['item_listcat'] = self.__parse_item_listcat(item)
        parsed['item_tag'] = self.__parse_item_tag(item)
        # Combat information
        parsed['item_damage'] = self.__parse_item_damage(item)
        parsed['item_damage_type'] = self.__parse_item_damage_type(item)
        parsed['item_defense'] = self.__parse_item_defense(item)
        parsed['item_velocity'] = self.__parse_item_velocity(item)
        parsed['item_knockback'] = self.__parse_item_knockback(item)
        # Purchase information
        parsed['item_buy_price'] = self.__parse_item_buy_price(item)
        parsed['item_sell_price'] = self.__parse_item_sell_price(item)
        # Tool information
        parsed['item_axe_power'] = self.__parse_item_axe_power(item)
        parsed['item_pickaxe_power'] = self.__parse_item_pickaxe_power(item)
        parsed['item_hammer_power'] = self.__parse_item_hammer_power(item)
        # Miscellaneous information
        parsed['item_tooltips'] = self.__parse_item_tooltips(item)
        parsed['item_hardmode'] = self.__parse_item_hardmode(item)
        return self.__process_item(parsed)

    def __parse_page_url(self, item: dict) -> str | None:
        content = soup(item['Page'], 'html.parser')
        if (a := content.select_one('a')):
            prefix = 'https://terraria.fandom.com'
            return prefix + a['href']
        else:
            return None

    def __parse_page_title(self, item: dict) -> str:
        content = soup(item['PageTitle'], 'html.parser')
        return content.select_one('p').text.strip()

    def __parse_page_id(self, item: dict) -> int:
        return int(item['PageID'].replace(',', ''))

    def __parse_item_id(self, item: dict) -> int:
        if not item['itemid']:
            return None
        return int(item['itemid'].replace(',', ''))

    def __parse_item_name(self, item: dict) -> str:
        return item['name']

    def __parse_item_internal_name(self, item: dict) -> str:
        return item['internalname']

    def __parse_item_image(self, item: dict) -> str | None:
        content = soup(item['image'], 'html.parser')
        if (img := content.select_one('img')):
            url = img['src']
            return url
        else:
            return None

    def __parse_item_image_placed(self, item: dict) -> str | None:
        content = soup(item['imageplaced'], 'html.parser')
        if (img := content.select_one('img')):
            url = img['src']
            return url
        else:
            return None

    def __parse_item_image_equipped(self, item: dict) -> str | None:
        content = soup(item['imageequipped'], 'html.parser')
        if (img := content.select_one('img')):
            url = img['src']
            return url
        else:
            return None

    def __parse_item_autoswing(self, item: dict) -> bool:
        return item['autoswing'] == 'Yes'

    def __parse_item_stack(self, item: dict) -> int:
        content = soup(item['stack'], 'html.parser')
        text = content.select_one('p')
        if not text:
            return 1
        text = text.text.strip()
        stack = text.split('/')[0].strip()
        return int(stack)

    def __parse_item_consumable(self, item: dict) -> bool:
        return item['consumable'] == 'Yes'

    def __parse_item_type(self, item: dict) -> list[str] | None:
        item_type = item['type']
        if not item_type:
            return None
        content = soup(item_type, 'html.parser')
        text = content.text.split('•')
        text = [t.strip().capitalize() for t in text]
        return text

    def __parse_item_listcat(self, item: dict) -> list[str] | None:
        listcat = item['listcat']
        if not listcat:
            return None
        content = soup(listcat, 'html.parser')
        text = content.text.split('•')
        text = [t.strip().capitalize() for t in text]
        return text

    def __parse_item_tag(self, item: dict) -> list[str] | None:
        tag = item['tag']
        if not tag:
            return None
        content = soup(tag, 'html.parser')
        text = content.text.strip()
        tags = text.split('•')
        misc = [
            (
                "vendor:Arms Dealer <span class=\"eico s i0 i1 i4\" "
                "title=\"PC, Console and Mobile versions\"><b><"
            ),
            (
                "vendor:Traveling Merchant <span class=\"eico s i2 i5 i7 i9 i10\" "
                "title=\"Old-gen console, Windows Phone, Old Chinese, tModLoader "
                "and tModLoader 1.3-Legacy versions\"><b>< "
            ),
            "b><i><",
            "i><",
            "span>"
        ]
        tags = filter(lambda t: t.strip() not in misc, tags)
        tags = [t.strip().capitalize() for t in tags]
        return tags

    def __parse_item_damage(self, item: dict) -> int | None:
        content = soup(item['damage'], 'html.parser')
        text = content.select_one('p')
        if text is None:
            return None
        text = text.text.strip()
        damage = text.split('/')[0].strip()
        damage = damage.split(' ')[0].strip()
        damage = damage.split('(')[0].strip()
        return int(damage)

    def __parse_item_damage_type(self, item: dict) -> str | None:
        text = item['damagetype'].split('\\')[0]
        return text.strip() if text else None

    def __parse_item_defense(self, item: dict) -> int | None:
        content = soup(item['defense'], 'html.parser')
        text = content.select_one('p')
        if text is None:
            return None
        text = text.text.strip()
        defense = text.split('/')[0].strip()
        defense = defense.split(' ')[0].strip()
        defense = defense.split('(')[0].strip()
        return int(defense)

    def __parse_item_velocity(self, item: dict) -> float | None:
        content = soup(item['velocity'], 'html.parser')
        text = content.select_one('p')
        if text is None:
            return None
        text = text.text.strip()
        velocity = text.split('/')[0].strip()
        velocity = velocity.split(' ')[0].strip()
        velocity = velocity.split('(')[0].strip()
        return float(velocity)

    def __parse_item_knockback(self, item: dict) -> float | None:
        content = soup(item['knockback'], 'html.parser')
        text = content.select_one('p')
        if text is None:
            return None
        text = text.text.strip()
        knockback = text.split('/')[0].strip()
        knockback = knockback.split(' ')[0].strip()
        knockback = knockback.split('(')[0].strip()
        return float(knockback)

    def __parse_item_buy_price(self, item: dict) -> tuple[int, str] | None:
        content = soup(item['buy'], 'html.parser')
        if (price := content.select_one('span.coin')):
            value = price['data-sort-value']
            currency = "coins"
        elif (price := content.select_one('span.coins')):
            value = price['title'].split()[0]
            currency = "medals"
        else:
            return None
        return (int(value), currency)

    def __parse_item_sell_price(self, item: dict) -> tuple[int, str] | None:
        content = soup(item['sell'], 'html.parser')
        if (price := content.select_one('span.coin')):
            value = price['data-sort-value']
            currency = "coins"
        else:
            return None
        return (int(value), currency)

    def __parse_item_axe_power(self, item: dict) -> int | None:
        power = item['axe']
        if not power:
            return None
        content = soup(power, 'html.parser')
        if content.select_one('span'):
            return None
        text = content.select_one('p').text.strip().strip('%')
        return int(text)

    def __parse_item_pickaxe_power(self, item: dict) -> int | None:
        power = item['pick']
        if not power:
            return None
        content = soup(power, 'html.parser')
        text = content.select_one('p').text.strip()
        text = text.split()[0].strip().strip('%')
        return int(text)

    def __parse_item_hammer_power(self, item: dict) -> int | None:
        power = item['hammer']
        if not power:
            return None
        content = soup(power, 'html.parser')
        text = content.select_one('p').text.strip().strip('%')
        return int(text)

    def __parse_item_tooltips(self, item: dict) -> list[str] | None:
        tooltip = item['tooltip']
        if not tooltip:
            return None
        content = soup(tooltip, 'html.parser')
        if (game_text := content.select_one('span.gameText')):
            tooltips = game_text.get_text(separator='+').split('+')
            tooltips = [t.strip(" \"\'") for t in tooltips]
            return tooltips
        else:
            return None

    def __parse_item_hardmode(self, item: dict) -> bool:
        return item['hardmode'] == 'Yes'

    def __process_item(self, item: dict) -> dict:
        all_tags = []
        if item['item_type']:
            all_tags.extend(item['item_type'])
        if item['item_listcat']:
            all_tags.extend(item['item_listcat'])
        if item['item_tag']:
            all_tags.extend(item['item_tag'])
        vendors = []
        tags_filtered = []
        for tag in all_tags:
            if tag.lower().startswith('vendor:'):
                vendor = tag[7:].split('<')[0].strip().capitalize()
                if 'ravelling' in vendor:
                    vendor = 'Traveling merchant'
                vendors.append(vendor)
            elif tag.replace(' ', '').isalpha():
                tags_filtered.append(tag.capitalize())
        item['item_vendors'] = vendors if vendors else None
        item['item_tags'] = tags_filtered if tags_filtered else None
        item.pop('item_type')
        item.pop('item_listcat')
        item.pop('item_tag')
        return item
