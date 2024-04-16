from scraper import Scraper
from bs4 import BeautifulSoup as soup


class DropScraper(Scraper):
    def __init__(
        self,
        url: str,
        cookies: dict = None,
        data_folder: str = None,
        cache_folder: str = None
    ):
        params = {}
        params['tables'] = 'Drops'
        params['fields'] = ','.join([
            "_pageName=Page",
            "nameraw=nameraw",
            "id=id",
            "name=name",
            "item=item",
            "quantity=quantity",
            "rate=rate",
            "custom=custom",
            "isfromnpc=isfromnpc",
            "normal=normal",
            "expert=expert",
            "master=master"])
        super().__init__(url, params, cookies, data_folder, cache_folder)

    def get_data(self) -> list[dict]:
        data = super().get_data()
        return filter(self.__filter_drop, data)

    def __filter_drop(self, drop: dict) -> bool:
        if not drop['normal'] == 'Yes':
            return False
        if 'Treasure Bag' in drop['nameraw']:
            return False
        def validate(span: soup) -> bool:
            if (sp := span.select_one('span.eico')):
                if 'pc' not in sp['title'].lower() and 'desktop' not in sp['title'].lower():
                    return False
            return True
        valid = True
        rate = soup(drop['rate'], 'html.parser')
        if (normal := rate.select_one('span.m-normal')):
            if not validate(normal):
                valid = False
            if (expert := rate.select_one('span.m-expert')):
                if not validate(expert):
                    valid = False
                if (master := rate.select_one('span.m-master')):
                    if not validate(master):
                        valid = False
            elif (exper_master := rate.select_one('span.m-expert-master')):
                if not validate(exper_master):
                    valid = False
        else:
            if not validate(rate):
                valid = False
        if not valid:
            return False
        return True

    def parse(self) -> list[dict]:
        data = self.get_data()
        parsed = []
        for drop in data:
            parsed.append(self.parse_drop(drop))
        parsed = self.remove_duplicates(parsed)
        return parsed

    def parse_drop(self, drop: dict) -> dict:
        parsed = {}
        parsed['drop_source'] = self.parse_drop_source(drop)
        parsed['drop_source_type'] = self.parse_drop_source_type(drop)
        parsed['drop_item'] = self.parse_drop_item(drop)
        parsed['drop_amount'] = self.parse_drop_amount(drop)
        parsed['drop_rate'] = self.parse_drop_rate(drop)
        return parsed

    def remove_duplicates(self, data: list[dict]) -> list[dict]:
        filtered = []
        for drop in data:
            if drop not in filtered:
                filtered.append(drop)
        return filtered

    def parse_drop_source(self, drop: dict) -> str:
        return drop['nameraw'].strip()

    def parse_drop_item(self, drop: dict) -> str:
        return drop['item'].strip()

    def parse_drop_source_type(self, drop: dict) -> str:
        if drop['isfromnpc'] == 'Yes':
            return 'npc'
        else:
            return 'chest'

    def parse_drop_amount(self, drop: dict) -> list[tuple[int, int]] | None:
        def difficulty_span(span: soup) -> tuple[int, int] | None:
            text = span.get_text(strip=True, separator='/')
            text = text.split('/')[0]
            text = text.split(' ')[0]
            text = text.strip(' ~')
            text = text.replace('–', '-')
            if '-' in text:
                text = text.split('-')
                min_amount = ''.join(c for c in text[0] if c.isdigit())
                max_amount = ''.join(c for c in text[1] if c.isdigit())
                if min_amount and max_amount:
                    return (int(min_amount), int(max_amount))
                else:
                    return None
            else:
                amount = ''.join(c for c in text if c.isdigit())
                if amount:
                    return (int(amount), int(amount))
                else:
                    return None

        content = soup(drop['quantity'], 'html.parser')
        if (normal := content.select_one('span.m-normal')):
            amount_normal = difficulty_span(normal)
            if (expert := content.select_one('span.m-expert')):
                master = content.select_one('span.m-master')
                amount_expert = difficulty_span(expert)
                amount_master = difficulty_span(master)
            elif (exper_master := content.select_one('span.m-expert-master')):
                amount_expert = difficulty_span(exper_master)
                amount_master = amount_expert
        else:
            amount_normal = difficulty_span(content)
            amount_expert = amount_normal
            amount_master = amount_normal

        if amount_normal and amount_expert and amount_master:
            return [amount_normal, amount_expert, amount_master]
        elif not amount_normal and not amount_expert and not amount_master:
            return None
        else:
            raise ValueError("Amounts not all None or all not None.")

    def parse_drop_rate(self, drop: dict) -> list[tuple[float, float]] | None:
        def difficulty_span(span: soup) -> tuple[float, float] | None:
            text = span.get_text(strip=True, separator='/')
            text = text.split('/')[0]
            text = text.split(' ')[0]
            text = text.strip(' ~')
            text = text.replace('–', '-')
            if '-' in text:
                text = text.split('-')
                min_rate = ''.join(c for c in text[0] if c.isdigit() or c == '.')
                max_rate = ''.join(c for c in text[1] if c.isdigit() or c == '.')
                if min_rate and max_rate:
                    return (float(min_rate), float(max_rate))
                else:
                    return None
            else:
                rate = ''.join(c for c in text if c.isdigit() or c == '.')
                if rate:
                    return (float(rate), float(rate))
                else:
                    return None

        content = soup(drop['rate'], 'html.parser')
        if (normal := content.select_one('span.m-normal')):
            rate_normal = difficulty_span(normal)
            if (expert := content.select_one('span.m-expert')):
                master = content.select_one('span.m-master')
                rate_expert = difficulty_span(expert)
                rate_master = difficulty_span(master)
            elif (exper_master := content.select_one('span.m-expert-master')):
                rate_expert = difficulty_span(exper_master)
                rate_master = rate_expert
        else:
            rate_normal = difficulty_span(content)
            rate_expert = rate_normal
            rate_master = rate_normal

        if rate_normal and rate_expert and rate_master:
            return [rate_normal, rate_expert, rate_master]
        elif not rate_normal and not rate_expert and not rate_master:
            return None
        else:
            raise ValueError("Rates not all None or all not None.")
