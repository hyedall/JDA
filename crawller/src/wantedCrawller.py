import json
import random
import time
import requests
from typing import List
from collections import Counter
from tqdm import tqdm
from config import JobPosting
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def wantedLinkCrawlling(url: str):
    # Chrome Driver Loading
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
        )
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(url)
    
    # 무한 스크롤
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    # 로딩이 안되어 끝이라고 판단할 수 있으므로 넣은 check
    check = False
    
    while True:
        # 스크롤을 화면 가장 아래로 내린다
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        
        # 페이지 로딩 대기
        time.sleep(random.uniform(1.0, 1.5))

        # 현재 문서 높이를 가져와서 저장
        curr_height = driver.execute_script("return document.body.scrollHeight")
        
        if (curr_height == last_height):
            # 끝인지 확인 후에도 끝이라고 판단되면 scroll 종료.
            if check: break
            # 끝인지 확인이 안되었다면 10초 대기 후 다시 한 번더 check.
            else:
                time.sleep(10)
                check = True
        else:
            # check 후 스크롤이 더 있다고 판단되면 check 다시 원상태로 False
            if check: check = False
            last_height = driver.execute_script("return document.body.scrollHeight")
    
    # 무한 스크롤 후 HTML 페이지 스크래핑
    html = driver.page_source
    soup = bs(html, 'html.parser')
    elements = soup.find_all(class_="Card_className__u5rsb")
    ids = [element.a['href'][4:] for element in tqdm(elements)]

    return ids

def wantedContentsCrawlling(id: str):
    api_url = f"https://www.wanted.co.kr/api/v4/jobs/{id}"
    data = requests.get(api_url).json()

    # 공고 url
    url = f"https://www.wanted.co.kr/wd/{id}"
    # 회사명
    company = data["job"]["company"]["name"]
    # 모집 직무
    position = data["job"]["position"]
    # 회사 소개, 업무 내용, 자격 요건, 우대 사항, 복지 및 혜택 등
    contents = {attr: data["job"]["detail"][attr] for attr in data["job"]["detail"]}
    # 회사 위치
    try:
        contents["address"] = data["job"]["address"]["location"]
    except KeyError:
        contents["address"] = None
    # 회사 태그
    try:
        contents["company_tags"] = [attr["title"] for attr in data["job"]["company_tags"]]
    except KeyError:
        contents["company_tags"] = None
    # 스킬 태그
    try:
        contents["skill_tags"] = [attr["title"] for attr in data["job"]["skill_tags"]]
    except KeyError:
        contents["skill_tags"] = None
    
    return JobPosting(url, company, position, contents)

def wantedIdClassify(wanted_ids: List[str]):
    url = "http://localhost:9200/wanted/_search"
    query = {
        "_source": ["url"],
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    headers = {'content-type': 'application/json'}
    
    data = requests.get(url=url, data=json.dumps(query), headers=headers).json()
    
    # 현재 elasticsearch에 저장 되어 있는 url 정보 가져옴.
    present_ids = [item["_source"]["url"][28:] for item in data["hits"]["hits"]]
    # 현재 정보와 크롤링한 정보에 대하여 Counter.
    counter = Counter(wanted_ids + present_ids)
    # 새롭게 크롤링된 정보만 분류.
    ids = [id for id in counter.keys() if counter[id] == 1]
    
    return ids
    
if __name__ == "__main__":
    # 공고 링크들이 있는 url
    url = "https://www.wanted.co.kr/wdlist/518?country=all&job_sort=company.response_rate_order&years=-1"
    # 원티드 링크만 크롤링
    wanted_ids = wantedLinkCrawlling(url)
    # 크롤링한 링크들 중 필요한 공고만 분류
    ids = wantedIdClassify(wanted_ids)
    
    # 필요한 공고들에 대해서 내용 크롤링하여 elasticsearch에 저장
    for id in tqdm(ids):
        posting = wantedContentsCrawlling(id)
        requests.post(url="http://localhost:9200/wanted/_doc", data=json.dumps(posting.__dict__), headers={'content-type': 'application/json'})
        time.sleep(random.uniform(1.5, 2.0))