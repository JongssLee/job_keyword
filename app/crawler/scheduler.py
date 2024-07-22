import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from kakao_crawler import KakaoCrawler
from kakaopay_crawler import KakaoPayCrawler
from base_crawler import BaseCrawler
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_URL = "mongodb://localhost:27017"
DB_NAME = "job_database"

async def merge_json_files(output_file, *input_files):
    merged_data = {}
    for file_name in input_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.update(data)
        except FileNotFoundError:
            print(f"{file_name} not found, skipping.")
    return merged_data
    

async def run_crawlers():
    try:
        # logger.info("Initializing crawlers...")
        kakao_crawler = KakaoCrawler(DB_URL, DB_NAME)
        kakao_pay_crawler = KakaoPayCrawler(DB_URL, DB_NAME)
        # merge_data = BaseCrawler(base_url="",db_url=DB_URL, db_name=DB_NAME, collection_name="all_jobs", json_file="all_jobs.json")

        # logger.info("Running crawlers...")
        await asyncio.gather(
            kakao_crawler.crawl(),
            kakao_pay_crawler.crawl()
        )
        # merge_data.save_to_db(await merge_json_files("all_jobs.json", "kakao_jobs.json", "kakaopay_jobs.json"))

        # logger.info("Crawlers finished")
    except Exception as e:
        logger.exception(f"Error in run_crawlers: {e}")

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_crawlers, 'interval', seconds=20)
    scheduler.start()

    print("Press Ctrl+C to exit")
    try:
        await asyncio.Future()  # This will run forever until interrupted
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())