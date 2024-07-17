import asyncio
from kakao_crawler import KakaoCrawler
from kakaopay_crawler import KakaoPayCrawler
import json

async def merge_json_files(output_file, *input_files):
    merged_data = {}
    for file_name in input_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.update(data)
        except FileNotFoundError:
            print(f"{file_name} not found, skipping.")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
    print(f"All data merged into {output_file}")

async def main():
    kakao_crawler = KakaoCrawler()
    kakao_pay_crawler = KakaoPayCrawler()

    await asyncio.gather(
        kakao_crawler.measure_time(),
        kakao_pay_crawler.measure_time()
    )

    await merge_json_files("all_jobs.json", "kakao_jobs.json", "kakaopay_jobs.json")

if __name__ == "__main__":
    asyncio.run(main())