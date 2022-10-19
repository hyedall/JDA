import json
import random
import time
import requests
from tqdm import tqdm
from config import JobPosting
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def wantedLinkScraping():
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
    driver.get("https://www.wanted.co.kr/wdlist/518?country=all&job_sort=company.response_rate_order&years=-1")
    
    # 무한 스크롤
    print("Scroll Start.")
    last_height = driver.execute_script("return document.body.scrollHeight")
    # 로딩이 안되어 끝이라고 판단할 수 있으므로 넣은 check
    check = False
    start = time.time()
    while True:
        # 스크롤을 화면 가장 아래로 내린다
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        
        # 페이지 로딩 대기
        time.sleep(1)

        # 현재 문서 높이를 가져와서 저장
        curr_height = driver.execute_script("return document.body.scrollHeight")
        
        if (curr_height == last_height):
            # 끝인지 확인 후에도 끝이라고 판단되면 scroll 종료.
            if check:
                break
            # 끝인지 확인이 안되었다면 5초 대기 후 다시 한 번더 check.
            else:
                time.sleep(5)
                check = True
        else:
            if check:
                check = False
            last_height = driver.execute_script("return document.body.scrollHeight")
    print(f"Scroll Done. [{time.time()-start} s]")
    
    # 무한 스크롤 후 HTML 페이지 스크래핑
    html = driver.page_source
    soup = bs(html, 'html.parser')
    elements = soup.find_all(class_="Card_className__u5rsb")
    ids = [element.a['href'][4:] for element in tqdm(elements)]
    # f"https://www.wanted.co.kr/api/v4/jobs{element.a['href'][3:]}"
    return ids

def wantedContentsScraping(url: str):
    data = requests.get(url).json()

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
    
    
if __name__ == "__main__":
    ## Test 용
    # links = ["https://www.wanted.co.kr/api/v4/jobs/123492", "https://www.wanted.co.kr/api/v4/jobs/133211"]
    ## 저장한 links
    with open('ids.txt', 'r', encoding='utf-8') as f:
        ids = [line.rstrip() for line in f]
    ## 실제 production links
    # ids = wantedLinkScraping()
    # with open('ids.txt', 'w', encoding='utf-8') as f:
    #     for id in ids:
    #         f.write(id + '\n')
    
    print("Scraping Start.")
    start_time = time.time()
    
    for id in tqdm(ids):
        api_url = f"https://www.wanted.co.kr/api/v4/jobs/{id}"
        posting = wantedContentsScraping(api_url)
        res = requests.post(url="http://localhost:9200/wanted/_doc", data=json.dumps(posting.__dict__), headers={'content-type': 'application/json'})
        time.sleep(random.uniform(1.0, 1.5))
    
    print(f"걸린 시간 : {time.time() - start_time}")