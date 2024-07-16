from base_crawler import BaseCrawler
import asyncio

class KakaoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://careers.kakao.com/jobs", "kakao_jobs.json")

    async def get_specific_info(self, url):
        html = await self.fetch_page(url, render_js=True)
        soup = self.parse_html(html)
        res = []
        dl = soup.find('dl', class_='list_info')
        dd = dl.find_all('dd')[1].text
        res.append(dd)
        div = soup.find('div', class_='cont_board board_detail')
        job_descriptions = div.find_all('p', class_='txt_cont')[3:5]
        for job_description in job_descriptions:
            jobs = job_description.find_all('li')
            for job in jobs:
                res.append(job.text)
        return res

    async def crawl(self):
        html = await self.fetch_page(self.base_url, render_js=True)
        soup = self.parse_html(html)
        job_list = soup.find('ul', class_='list_jobs')
        job_data = []
        if job_list:
            jobs = job_list.find_all('a')
            tasks = []
            for job in jobs:
                link = job['href']
                title = job.find('h4', class_='tit_jobs').text
                work_experience = '경력' if '경력' in title else '신입'
                specific_url = f"https://careers.kakao.com{link}"
                tasks.append(self.get_specific_info(specific_url))
            
            job_details_list = await asyncio.gather(*tasks)
            
            for job, job_details in zip(jobs, job_details_list):
                title = job.find('h4', class_='tit_jobs').text
                work_experience = '경력' if '경력' in title else '신입'
                job_info = {
                    title: {
                        "직군": "테크",
                        "신입/경력": work_experience,
                        "근무형태": job_details[0],
                        "직무내용": job_details[1:]
                    }
                }
                job_data.append(job_info)
            await self.save_to_json({"카카오": job_data})