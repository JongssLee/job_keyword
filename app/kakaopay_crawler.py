from base_crawler import BaseCrawler
import asyncio

class KakaoPayCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://kakaopay.career.greetinghr.com/main", "kakaopay_jobs.json")

    async def get_specific_info(self, url):
        html = await self.fetch_page(url)
        soup = self.parse_html(html)
        div = soup.find('div', class_='ql-editor')
        job_description = div.find_all('h3')[2]
        job_details = []
        if job_description:
            current = job_description.next_sibling
            while current and current.name != 'h3':
                if current.name == 'ul':
                    for li in current.find_all('li'):
                        job_details.append(li.text.strip())
                current = current.next_sibling
        return job_details

    async def crawl(self):
        html = await self.fetch_page(self.base_url)
        soup = self.parse_html(html)
        ul = soup.find('ul', class_='Flex__FlexCol-sc-uu75bp-1 iKWWXF')
        job_data = []
        if ul:
            links = ul.find_all('a')
            tasks = []
            for link in links:
                specific_url = f"https://kakaopay.career.greetinghr.com{link['href']}"
                tasks.append(self.get_specific_info(specific_url))
            
            job_details_list = await asyncio.gather(*tasks)
            
            for link, job_details in zip(links, job_details_list):
                title = link.find('div', class_='Textstyled__Text-sc-55g6e4-0 dYCGQ').text
                spans = link.find_all('span', class_='Textstyled__Text-sc-55g6e4-0 gDzMae')
                span_contents = [span.text for span in spans]
                job_info = {
                    title: {
                        "직군": span_contents[0] if len(span_contents) > 0 else "",
                        "신입/경력": span_contents[1] if len(span_contents) > 1 else "",
                        "근무형태": span_contents[2] if len(span_contents) > 2 else "",
                        "직무내용": job_details
                    }
                }
                job_data.append(job_info)
            await self.save_to_json({"카카오페이": job_data})