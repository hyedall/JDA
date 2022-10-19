# JobPostingSearch
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3910/)


**JobPostingSearch**는 IT 채용 공고 데이터를 활용하여 원하는 공고를 빠르게 찾을 수 있도록 통합적으로 검색할 수 있는 API를 구현하기 위해 데이터 파이프라인을 만든 프로젝트입니다.


<!-- TABLE OF CONTENTS -->
## Tables

* [Architecture diagram](#architecture-diagram)
* [How it works](#how-it-works)
    * [Data scraping](#data-scraping)
    * [Data flow](#data-flow)
    * [Data access](#data-access)
* [Prerequisites](#prerequisites)
* [Running project](#running-project)
* [API service](#api-service)
* [Insert Job Posting Scraping DAG](#insert-job-posting-scraping-dag)

<!-- ARCHITECTURE DIAGRAM -->
## Architecture Diagram
![System Architecture](./img/Architecture.png)


<!-- HOW IT WORKS -->
## How it works

#### Data Scraping
각 **DAG**들은 IT 회사의 채용 공고를 스크래핑 후 **ETL**하는 DAG이다.
- task1 : 각 IT 회사 웹사이트의 채용 공고 게시물을 **Scraping**하여 파이썬 객체로 직렬화한다.
- task2 : task1의 데이터를 **Transform**한다.
- task3 : task2의 데이터를 **MongoDB**로 **Load**한다.

#### Data flow
- **Airflow DAG**를 통해 각 데이터가 **MongoDB**의 각 **collection**으로 저장된다.
- **Python**으로 작성한 스크립트로 **APScheduler**를 이용하여 만든 스케줄러가 **MongoDB**의 각 **collection documents**를 통합하여 **Elasticsearch**의 하나의 인덱스로 저장한다.

#### Data access
- 파이썬 웹 프레임워크 **Flask**로 접근할 수 있다.

## Prerequisites
프로젝트를 실행시키기 위해 필요한 소프트웨어.

### Install:
- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.9+ (pip)](https://www.python.org/)
- [docker-compose](https://docs.docker.com/compose/install/)

## Running project
`manage.sh` 스크립트는 `docker-compose`를 작동시키기 위한 Shell 스크립트입니다.

- Build project infrastructure

```sh
./manage.sh start
```

- Stop project infrastructure

```sh
./manage.sh stop
```

- Down project infrastructure

```sh
./manage.sh down
```

## API service
- 모든 채용 공고
```
[GET] http://127.0.0.1:5000/postings
```

- 채용 공고 검색
```
[GET] http://127.0.0.1:5000/postings?search=keyword
```

## Insert Job Posting Scraping DAG
다른 회사의 채용 공고를 추가하려면 그 회사의 채용 공고를 스크래핑하는 파이썬 스크립트를 작성해야 합니다.
### Required Python Script
1. **/airflow/modules/job_posting_scraper/company_job_posting_scraping.py**
- **JobPostingRecord** 객체의 **get_dict_posting()** 한 데이터를 **return** 해야합니다.
```python
def company_job_positng_scraping():
   ...
   serialized_data = [posting.get_dict_posting() for posting in job_postings]
   
   return serialized_data
```
2. **/airflow/modules/config/config.py**
- **Config**의 **JOB_POSTINGS**에 스크래핑에 필요한 정보 추가
```python
class Config:
   ...
   
   JOB_POSTINGS = {
      ...,
      'company': {
         'url': ...,
         'posting_css_selector': ...,
         ...
      }
   }
```
3. **/airflow/dags/company_dag.py**
- **t1**이 채용 공고를 스크랩하는 **task**입니다. **t2**와 **t3**는 고정되어 있습니다. 
```python
...
with DAG(
    dag_id='company_job_posting_ETL',
    description='company job postings scraping DAG',
    start_date=datetime(now.year, now.month, now.day),
    schedule_interval=timedelta(hours=12)
) as dag:
    t1 = PythonOperator(
        task_id='job_posting_scraping',
        python_callable=company_job_posting_scraping,
        provide_context=True,
        owner='DAG_owner',
        retries=3,
        retry_delay=timedelta(minutes=1)
    )
    t2 = ...
    
    t3 = ...
    t1 >> t2 >> t3
```