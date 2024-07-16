from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
session = HTMLSession()

def get_specific_info(url):
    r = session.get(url)
    res = []
    # JavaScript 실행
    r.html.render(sleep=5, keep_page=True)

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(r.html.html, 'html.parser')
    dl = soup.find('dl', class_='list_info')
    dd = dl.find_all('dd')[1].text
    res.append(dd)
    div = soup.find('div', class_='cont_board board_detail')

    job_descriptions = div.find_all('p', class_='txt_cont')
    job_descriptions = job_descriptions[3:5]
    for job_description in job_descriptions:
        jobs = job_description.find_all('li')
        for job in jobs:
            res.append(job.text)

    return res

    



url = "https://careers.kakao.com/jobs?skillSet=&part=TECHNOLOGY&company=KAKAO&keyword=&employeeType=&page=1"
r = session.get(url)

# JavaScript 실행
r.html.render(sleep=5, keep_page=True)

# BeautifulSoup으로 파싱
soup = BeautifulSoup(r.html.html, 'html.parser')

# 원하는 요소 찾기
job_list = soup.find('ul', class_='list_jobs')
if job_list:

    jobs = job_list.find_all('a')
    job_data = []
    for job in jobs:
        link = job['href']
        # print(link)
        title = job.find('h4', class_='tit_jobs')
        work_experience = '신입'
        if title:
            print(title.text)
            if '경력' in title.text:
                work_experience = '경력'
        specific_url = 'https://careers.kakao.com'+link
        job_details = get_specific_info(specific_url)
        print(job_details)
        job_info = {
            "직군": "테크",
            "신입/경력": work_experience,
            "근무형태": job_details[0],
            "직무내용": job_details[1:]
        }
        job_info = {
            title.text: job_info
        }
        print(job_info)
        job_data.append(job_info)
    job_data = {
        "카카오": job_data
    }
    
    with open('job_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.update(job_data)
    with open('job_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

