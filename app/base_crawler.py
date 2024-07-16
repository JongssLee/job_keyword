import aiohttp
from bs4 import BeautifulSoup
import json
import time
import asyncio

class BaseCrawler:
    def __init__(self, base_url, json_file):
        self.base_url = base_url
        self.json_file = json_file

    async def fetch_page(self, url, render_js=False):
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                html = await response.text()
                if render_js:
                    # Note: JavaScript rendering might require additional tools like Playwright
                    pass
                return html

    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    async def save_to_json(self, data):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = {}

        existing_data.update(data)

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.json_file}")

    async def get_specific_info(self, url):
        raise NotImplementedError("Subclasses should implement this method")

    async def crawl(self):
        raise NotImplementedError("Subclasses should implement this method")

    async def measure_time(self):
        start_time = time.time()
        await self.crawl()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{self.__class__.__name__} execution time: {elapsed_time:.2f} seconds")
        return elapsed_time