from scraper import Scraper
from bs4 import BeautifulSoup as soup


class NpcScraper(Scraper):
    def __init__(
        self,
        url: str,
        cookies: dict = None,
        data_folder: str = None,
        cache_folder: str = None
    ):
        params = {}
        params['tables'] = 'NPCs'
        params['fields'] = ','.join([
            "_pageName=Page",
            "name=name",
            "nameraw=nameraw",
            "image=image",
            "types__full=types",
            "categories__full=categories",
            "hardmode=hardmode",
            "expert=expert",
            "master=master",
            "variant=variant",
            "environment=environment",
            "ai=ai",
            "damage=damage",
            "life=life",
            "defense=defense",
            "knockback=knockback",
            "banner=banner",
            "bannername=bannername",
            "money=money",
            "npcid=npcid",
            "immunities__full=immunities"])
        super().__init__(url, params, cookies, data_folder, cache_folder)

    def get_data(self) -> list[dict]:
        data = super().get_data()
        return filter(self.__filter_npc, data)

    def __filter_npc(self, npc: dict) -> bool:
        return True

    def parse(self) -> list[dict]:
        data = self.get_data()
        parsed = []
        for npc in data:
            parsed.append(self.parse_npc(npc))
        return parsed

    def parse_npc(self, npc: dict) -> dict:
        parsed = {}
        parsed['npc_name'] = self.parse_npc_name(npc)
        parsed['npc_image'] = self.parse_npc_image(npc)
        parsed['npc_hardmode'] = self.parse_npc_hardmode(npc)
        parsed['npc_environment'] = self.parse_npc_environment(npc)
        return parsed

    def parse_npc_name(self, npc: dict) -> str:
        content = soup(npc['name'], 'html.parser')
        return content.get_text(strip=True, separator=' ')

    def parse_npc_image(self, npc: dict) -> str:
        content = soup(npc['image'], 'html.parser')
        img = content.find('img')
        return img['src']

    def parse_npc_hardmode(self, npc: dict) -> bool:
        return npc['hardmode'] == 'Yes'

    def parse_npc_environment(self, npc: dict) -> list[str]:
        environment = npc['environment']
        if environment == '':
            return []
        if '+' in environment:
            environment = environment.split('+')
        else:
            environment = [environment]
        environments = []
        for env in environment:
            if '/' in env:
                environments.extend(env.split('/'))
            else:
                environments.append(env)
        return [env.strip().capitalize() for env in environments]
