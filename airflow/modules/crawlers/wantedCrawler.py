import sys
import os
sys.path.append(os.environ["AIRFLOW_HOME"])
import random
import time
import requests
from collections import defaultdict
from pymongo import MongoClient
from typing import List
from tqdm import tqdm
from modules.config import JobPosting, MONGO_HOST, MONGO_PORT
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def wantedLinkCrawling():
    url = "https://www.wanted.co.kr/wdlist/518?country=all&job_sort=company.response_rate_order&years=-1"

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

def wantedContentsCrawling(id: str):
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
    
    return JobPosting(id, url, company, position, contents)

def wantedIdClassify(wanted_ids: List[str], client: MongoClient):
    db = client.JDA
    collection = db.wanted
    tmp = defaultdict(int)

    # 현재 Mongo DB에 저장 되어 있는 공고들의 id 정보 가져옴.
    for posting in collection.find({"validation": True}): tmp[posting["id"]] = -1
    # 현재 DB 데이터와 wanted 데이터에 대해 분류 Dictionary
    for wanted_id in wanted_ids: tmp[wanted_id] += 1

    return tmp

def wantedJdCrawling(**context):
    # Mongo DB Client
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    # 원티드 링크만 크롤링
    wanted_ids = context['ti'].xcom_pull(task_ids='wantedLinkCrawling')
    # 크롤링한 링크들 중 삽입할 공고, 비활성화할 공고 분류
    ids = wantedIdClassify(wanted_ids, client)
    postings = {
        "insert": [],
        "update": []
    }
    for id in tqdm(ids):
        if ids[id] == 1:
            posting = wantedContentsCrawling(id)
            postings["insert"].append(posting.__dict__)
            time.sleep(random.uniform(1.5, 2.0))
        elif ids[id] == -1:
            postings["update"].append(id)
    
    return postings