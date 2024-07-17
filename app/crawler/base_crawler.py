from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bs4 import BeautifulSoup
import time
import aiohttp
import pyppeteer
import json

class BaseCrawler:
    def __init__(self, base_url, db_url, db_name, collection_name, json_file):
        self.base_url = base_url
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.json_file = json_file

    async def fetch_page(self, url, render_js=False):
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                html = await response.text()
                if render_js:
                    #rendering js
                    browser = await pyppeteer.launch()
                    page = await browser.newPage()
                    await page.goto(url)
                    await asyncio.sleep(5)
                    html = await page.content()
                    await browser.close()

                return html

    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')


    async def save_to_db(self, data):
        await self.collection.delete_many({})  # 기존 데이터 삭제
        if isinstance(data, list):
            await self.collection.insert_many(data)
        else:
            await self.collection.insert_one(data)
        print(f"Data saved to MongoDB collection: {self.collection.name}")

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