from bs4 import BeautifulSoup as soup
import requests
import os
import json


def soup_layout(element: soup) -> str:
    layout = f'<{element.name}'
    class_attr = element.get('class')
    if class_attr:
        layout += '.' + '.'.join(class_attr)
    layout += '>'
    for child in element.findChildren(recursive=False):
        layout += soup_layout(child)
    layout += f'</{element.name}>'
    return layout


class Scraper:
    def __init__(
        self,
        url: str,
        params: dict = None,
        cookies: dict = None,
        data_folder: str = None,
        cache_folder: str = None
    ):
        self.url = url
        self.params = params
        self.cookies = cookies
        self.data_folder = data_folder
        self.cache_folder = cache_folder

    def __str__(self) -> str:
        return self.name()

    def name(self) -> str:
        range_str = f"{self.params['offset']+1}-{self.params['offset']+self.params['limit']}"
        return f"{self.params['tables']}-{range_str}"

    def page_type(self) -> str:
        return self.params['tables']

    def get_page(self) -> soup:
        cache_folder = os.path.join(self.cache_folder, self.page_type())
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)
        cache_file = os.path.join(cache_folder, f"{self.name()}.html")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                content = soup(f.read(), 'html.parser')
        else:
            content = self.get_soup()
            with open(cache_file, 'wb') as f:
                f.write(content.encode('utf-8'))
        return content

    def get_soup(self) -> soup:
        print(f"Scraping {self.name()}...")
        response = requests.get(self.url, params=self.params, cookies=self.cookies)
        content = soup(response.text, 'html.parser')
        content = content.select_one('div.mw-spcontent')
        return content

    def scrape(self) -> list[dict]:
        self.params['offset'] = 0
        self.params['limit'] = 500
        soup = self.get_page()
        data = []
        while (table := soup.select_one('table.cargoTable')):
            column_names = []
            for th in table.select_one('thead > tr').select('th'):
                column_names.append(th.text)
            for row in table.select_one('tbody').select('tr:has(td[class])'):
                row_data = {}
                for i, td in enumerate(row.select('td[class]')):
                    row_data[column_names[i]] = td.decode_contents()
                data.append(row_data)
            self.params['offset'] += self.params['limit']
            soup = self.get_page()
        return data

    def get_data(self) -> list[dict]:
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        data_file = os.path.join(self.data_folder, f"{self.page_type()}_raw.json")
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = self.scrape()
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4)
        return data

    def get_parsed_data(self) -> list[dict]:
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        data_file = os.path.join(self.data_folder, f"{self.page_type()}_parsed.json")
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = self.parse()
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4)
        return data

    def field_layouts(self, field: str) -> dict:
        layouts = {}
        for row in self.get_data():
            if field not in row:
                raise ValueError(f"Field '{field}' not in row.")
            value = row[field]
            layout = soup_layout(soup(value, 'html.parser'))
            if layout not in layouts:
                layouts[layout] = {'count': 1, 'fields': [value]}
            else:
                layouts[layout]['count'] += 1
                layouts[layout]['fields'].append(value)
        return layouts

    def print_field_layouts(self, field: str):
        layouts = self.field_layouts(field)
        s = soup("<head></head><body></body>", "html.parser")
        for layout in layouts:
            ul = soup('<ul>', 'html.parser')
            fields = layouts[layout]['fields']
            fields = list(set(fields))
            fields.sort()
            for field in fields:
                field = field.replace('\n', '↵').replace('\t', '⇥').replace('\r', '↵')
                li = soup('<li>', 'html.parser')
                li.li.append(soup(field, 'html.parser'))
                ul.ul.append(li)
            s.body.append(ul)
        out = "out.html"
        with open(out, 'wb') as f:
            f.write(s.encode('utf-8'))
