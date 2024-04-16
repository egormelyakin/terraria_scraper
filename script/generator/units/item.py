from dataclasses import dataclass
from enum import StrEnum

from info_list import InfoList
from node import Node, NodeType


class Currency(StrEnum):
    COINS = "Coins"
    MEDALS = "Medals"


class DamageType(StrEnum):
    MELEE = "Melee"
    RANGED = "Ranged"
    MAGIC = "Magic"
    SUMMON = "Summon"


class Vendor(StrEnum):
    ARMS_DEALER = "Arms Dealer"
    CLOTHIER = "Clothier"
    CYBORG = "Cyborg"
    DEMOLITIONIST = "Demolitionist"
    DRYAD = "Dryad"
    DYE_TRADER = "Dye Trader"
    GOBLIN_TINKERER = "Goblin Tinkerer"
    GOLFER = "Golfer"
    GUIDE = "Guide"
    MECHANIC = "Mechanic"
    MERCHANT = "Merchant"
    PAINTER = "Painter"
    PARTY_GIRL = "Party Girl"
    PIRATE = "Pirate"
    PRINCESS = "Princess"
    SANTA_CLAUS = "Santa Claus"
    SKELETON_MERCHANT = "Skeleton Merchant"
    STEAMPUNKER = "Steampunker"
    STYLIST = "Stylist"
    TAVERNKEEP = "Tavernkeep"
    TRAVELING_MERCHANT = "Traveling Merchant"
    TRUFFLE = "Truffle"
    WITCH_DOCTOR = "Witch Doctor"
    WIZARD = "Wizard"
    ZOOLOGIST = "Zoologist"


@dataclass
class Price:
    amount: int
    currency: Currency


@dataclass
class Item:
    page_url: str | None = None
    page_title: str = None
    page_id: int = None
    items_id: int = None
    item_name: str = None
    item_internal_name: str = None
    item_image: str | None = None
    item_image_placed: str | None = None
    item_image_equipped: str | None = None
    item_autoswing: bool = None
    item_stack: int = None
    item_consumable: bool = None
    item_damage: int | None = None
    item_damage_type: DamageType | None = None
    item_defense: int | None = None
    item_velocity: float | None = None
    item_knockback: float | None = None
    item_buy_price: Price | None = None
    item_sell_price: Price | None = None
    item_axe_power: int | None = None
    item_pickaxe_power: int | None = None
    item_hammer_power: int | None = None
    item_tooltips: list[str] | None = None
    item_hardmode: bool = None
    item_vendors: list[str] | None = None
    item_tags: list[str] | None = None

    def init_from_data(self, data: dict):
        self.page_url = data.get("page_url")
        self.page_title = data.get("page_title")
        self.page_id = data.get("page_id")
        self.items_id = data.get("items_id")
        self.item_name = data.get("item_name")
        self.item_internal_name = data.get("item_internal_name")
        self.item_image = data.get("item_image")
        self.item_image_placed = data.get("item_image_placed")
        self.item_image_equipped = data.get("item_image_equipped")
        self.item_autoswing = data.get("item_autoswing")
        self.item_stack = data.get("item_stack")
        self.item_consumable = data.get("item_consumable")
        self.item_damage = data.get("item_damage")
        if data.get("item_damage_type") is not None:
            damage_type = data.get("item_damage_type").lower()
            for damage_type_enum in DamageType:
                if damage_type_enum.value.lower() == damage_type:
                    self.item_damage_type = damage_type_enum
        self.item_defense = data.get("item_defense")
        self.item_velocity = data.get("item_velocity")
        self.item_knockback = data.get("item_knockback")
        if data.get("item_buy_price") is not None:
            amount, currency = data.get("item_buy_price")
            currency = currency.lower()
            for currency_enum in Currency:
                if currency_enum.value.lower() == currency:
                    self.item_buy_price = Price(amount, currency_enum)
        if data.get("item_sell_price") is not None:
            amount, currency = data.get("item_sell_price")
            currency = currency.lower()
            for currency_enum in Currency:
                if currency_enum.value.lower() == currency:
                    self.item_sell_price = Price(amount, currency_enum)
        self.item_axe_power = data.get("item_axe_power")
        self.item_pickaxe_power = data.get("item_pickaxe_power")
        self.item_hammer_power = data.get("item_hammer_power")
        self.item_tooltips = data.get("item_tooltips")
        self.item_hardmode = data.get("item_hardmode")
        if data.get("item_vendors") is not None:
            self.item_vendors = []
            for vendor in data.get("item_vendors"):
                vendor = vendor.lower()
                for vendor_enum in Vendor:
                    if vendor_enum.value.lower() == vendor:
                        self.item_vendors.append(vendor_enum)
        self.item_tags = data.get("item_tags")

    def __str__(self):
        return f'(ITEM) {self.item_name} ({self.item_internal_name})'


class Items(InfoList):
    def __init__(self, content: list[dict]):
        items = []
        for item_data in content:
            item = Item()
            item.init_from_data(item_data)
            items.append(item)
        super().__init__(items, "item_name")
