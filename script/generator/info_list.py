class InfoList:
    def __init__(self, content: list, sort_key: str):
        self.content = content
        self.sort_key = sort_key
        self.content.sort(key=lambda x: getattr(x, self.sort_key).lower())

    def get_items(self, key: str, value: str) -> list:
        if key == self.sort_key:
            return self.binary_search(value)
        else:
            return self.linear_search(key, value)

    def get_item(self, key: str, value: str):
        items = self.get_items(key, value)
        if len(items) == 0:
            return None
        else:
            return items[0]

    def binary_search(self, value: str) -> list:
        a, b = 0, len(self.content) - 1
        while a <= b:
            mid = (a + b) // 2
            if getattr(self.content[mid], self.sort_key).lower() < value.lower():
                a = mid + 1
            elif getattr(self.content[mid], self.sort_key).lower() > value.lower():
                b = mid - 1
            else:
                return self.get_items_by_index(mid)
        return []

    def linear_search(self, key: str, value: str) -> list:
        items = []
        for item in self.content:
            if getattr(item, key) == value:
                items.append(item)
        return items

    def get_items_by_index(self, index: int) -> list:
        items = []
        value = getattr(self.content[index], self.sort_key).lower()
        for i in range(index, len(self.content)):
            if getattr(self.content[i], self.sort_key).lower() == value:
                items.append(self.content[i])
            else:
                break
        for i in range(index - 1, -1, -1):
            if getattr(self.content[i], self.sort_key).lower() == value:
                items.append(self.content[i])
            else:
                break
        return items

    def __str__(self):
        return self.content.__str__()

    def __repr__(self):
        return self.content.__repr__()

    def __getitem__(self, item):
        return self.content[item]

    def __len__(self):
        return len(self.content)
