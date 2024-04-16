from scraper import Scraper


class RecipeScraper(Scraper):
    def __init__(
        self,
        url: str,
        cookies: dict = None,
        data_folder: str = None,
        cache_folder: str = None
    ):
        params = {}
        params['tables'] = 'Recipes'
        params['fields'] = ','.join([
            "_pageName=Page",
            "result=result",
            "resultid=resultid",
            "resultimage=resultimage",
            "resulttext=resulttext",
            "amount=amount",
            "version=version",
            "station=station",
            "ingredients__full=ingredients",
            "ings=ings",
            "args=args"])
        super().__init__(url, params, cookies, data_folder, cache_folder)

    def get_data(self) -> list[dict]:
        data = super().get_data()
        return filter(self.__filter_recipe, data)

    def __filter_recipe(self, recipe: dict) -> bool:
        station = recipe['station']
        if 'shimmer' in station.lower():
            return False
        version = recipe['version']
        if not version:
            return True
        return 'pc' in version.lower()

    def parse(self) -> list[dict]:
        data = self.get_data()
        parsed = []
        for recipe in data:
            parsed.append(self.parse_recipe(recipe))
        return parsed

    def parse_recipe(self, recipe: dict) -> dict:
        parsed = {}
        parsed['recipe_result'] = self.parse_recipe_result(recipe)
        parsed['recipe_ingredients'] = self.parse_recipe_ingredients(recipe)
        parsed['recipe_station'] = self.parse_recipe_station(recipe)
        return parsed

    def parse_recipe_result(self, recipe: dict) -> tuple[str, int]:
        name = recipe['result'].strip()
        amount = int(recipe['amount'])
        return (name, amount)

    def parse_recipe_ingredients(self, recipe: dict) -> list[tuple[str, int]]:
        ingredients = recipe['args'].strip()
        ingredients = ingredients.split('^')
        parsed = []
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            name, amount = ingredient.split('¦')
            amount = int(amount)
            parsed.append((name, amount))
        return parsed

    def parse_recipe_station(self, recipe: dict) -> list[str]:
        stations = recipe['station'].strip()
        stations = stations.split(' and ')
        parsed = []
        for station in stations:
            station = station.strip()
            parsed.append(station)
        return parsed
