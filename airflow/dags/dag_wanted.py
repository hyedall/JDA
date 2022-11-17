import sys
import os
sys.path.append(os.environ["AIRFLOW_HOME"])

from airflow import DAG
from airflow.operators.python import PythonOperator
from modules.crawlers.wantedCrawler import wantedLinkCrawling, wantedJdCrawling
from modules.loaders.mongoLoader import mongoLoad
from modules.loaders.esLoader import esLoad
from datetime import timedelta, datetime

now = datetime.now()

with DAG(
    dag_id='wanted_crawling_dag',
    description='원티드 공고 크롤링 DAG',
    start_date=datetime(now.year, now.month, now.day),
    schedule_interval=timedelta(days=1),
    default_args={
        'owner': 'mungiyo',
        'retries': 3,
        'retry_delay': timedelta(minutes=1),
        'provide_context': True,
    }
) as dag:
    # Task1, 원티드 JD URL 크롤링
    t1 = PythonOperator(
        task_id='wantedLinkCrawling',
        python_callable=wantedLinkCrawling,
    )

    # Task2, 원티드 JD 크롤링
    t2 = PythonOperator(
        task_id='wantedJdCrawling',
        python_callable=wantedJdCrawling,
    )

    # Task3, JD Load to MongoDB
    t3 = PythonOperator(
        task_id='mongoLoad',
        python_callable=mongoLoad
    )

    # Task4, MongoDB to Elasticsearch
    t4 = PythonOperator(
        task_id='esLoad',
        python_callable=esLoad
    )


    t1 >> t2 >> t3 >> t4