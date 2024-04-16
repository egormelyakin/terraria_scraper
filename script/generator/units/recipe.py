from dataclasses import dataclass

from info_list import InfoList


@dataclass
class RecipeItem:
    item_name: str
    amount: int


@dataclass
class Recipe:
    recipe_result_item: str = None
    recipe_result_amount: int = None
    recipe_ingredients: list[RecipeItem] = None
    recipe_station: list[str] = None

    def init_from_data(self, data: dict):
        self.recipe_result_item = data["recipe_result"][0]
        self.recipe_result_amount = data["recipe_result"][1]
        self.recipe_ingredients = []
        for ingredient in data["recipe_ingredients"]:
            self.recipe_ingredients.append(RecipeItem(ingredient[0], ingredient[1]))
        self.recipe_station = data["recipe_station"]

    def __str__(self):
        string = '(RECIPE) '
        string += " + ".join([
            f'{ingredient.amount} {ingredient.item_name}'
            if ingredient.amount > 1 else ingredient.item_name
            for ingredient in self.recipe_ingredients
        ])
        if self.recipe_result_amount > 1:
            string += f' = {self.recipe_result_amount} {self.recipe_result_item}'
        else:
            string += f' = {self.recipe_result_item}'
        string += f' ({", ".join(self.recipe_station)})'
        return string


class Recipes(InfoList):
    def __init__(self, content: list[dict]):
        recipes = []
        for recipe_data in content:
            recipe = Recipe()
            recipe.init_from_data(recipe_data)
            recipes.append(recipe)
        super().__init__(recipes, "recipe_result_item")
