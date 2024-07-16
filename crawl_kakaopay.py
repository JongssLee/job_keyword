import requests
from bs4 import BeautifulSoup
import json
def get_job_info(url):
    # 웹 페이지의 내용을 가져옵니다
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoup 객체를 생성합니다
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)
    # ul 클래스를 찾습니다
    ul = soup.find('ul', class_='Flex__FlexCol-sc-uu75bp-1 iKWWXF')

    if ul is None:
        print("지정된 클래스의 ul 요소를 찾을 수 없습니다.")
        return


    links = ul.find_all('a')
    # ul 안의 모든 li 요소를 찾습니다
    lis = ul.find_all('li')
    job_data = []
    for link in links:
        # 각 li 안의 모든 span 요소를 찾습니다
        #print href
        specific_url = "https://kakaopay.career.greetinghr.com" + link['href']
        title = link.find('div', class_='Textstyled__Text-sc-55g6e4-0 dYCGQ').text
        
        spans = link.find_all('span', class_='Textstyled__Text-sc-55g6e4-0 gDzMae')
        
        job_details = get_specific_info(specific_url)
        # span의 텍스트 내용을 리스트로 만듭니다
        span_contents = [span.text for span in spans]
        job_info = {
            "직군": span_contents[0] if len(span_contents) > 0 else "",
            "신입/경력": span_contents[1] if len(span_contents) > 1 else "",
            "근무형태": span_contents[2] if len(span_contents) > 2 else "",
            "직무내용": job_details
        }
        job_info = {
            title: job_info
        }
        job_data.append(job_info)
        # 결과 출력
        # print(span_contents)
    job_data = {
        "카카오페이": job_data
    }
    save_to_json(job_data, "job_data.json")

def get_specific_info(url):
    # 웹 페이지의 내용을 가져옵니다
    response = requests.get(url)
    html_content = response.text

    # BeautifulSoup 객체를 생성합니다
    soup = BeautifulSoup(html_content, 'html.parser')
    # '직무소개' 섹션 찾기
    div = soup.find('div', class_='ql-editor')
    job_description = div.find_all('h3')[2]
    # print(job_description.text)
    if job_description:
        job_details = []
        current = job_description.next_sibling
       
        # 다음 h3 태그를 만날 때까지 순회
        while current and current.name != 'h3':
            
            if current.name == 'ul':
                for li in current.find_all('li'):
                    job_details.append(li.text.strip())
                
            current = current.next_sibling

        return job_details
    else:
        return []
    
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"데이터가 {filename}에 저장되었습니다.")

# 함수 사용 예시
url = "https://kakaopay.career.greetinghr.com/main#8252bf6b-714c-4885-8b81-3942163f3a50"  # 실제 크롤링할 URL로 변경해주세요
get_job_info(url)