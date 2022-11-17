import sys
import os
sys.path.append(os.environ["AIRFLOW_HOME"])
from modules.config import MONGO_HOST, MONGO_PORT, ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
from elasticsearch import Elasticsearch, helpers
from pymongo import MongoClient

# MongoDB 데이터 가져오기
def mongoFetch(client: MongoClient, db: str, collection: str, query: dict=None):
    mydb = client[db]
    mycollection = mydb[collection]

    data = list(mycollection.find(query))

    return data

# MongoDB의 데이터를 ES로 적재
def esLoad():
    mongo = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    es = Elasticsearch(f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}")
    db = "JDA"
    collection = "wanted"
    mongo_query = {"validation": True}

    es.delete_by_query(index="wanted", body={"query": {"match_all": {}}})
    mongo_data = mongoFetch(mongo, db, collection, mongo_query)
    docs = []
    for data in mongo_data:
        doc = {
            "_index": "wanted",
            "_id": str(data["_id"]),
            "_source": {
                "id": data["id"],
                "url": data["url"],
                "position": data["position"],
                "company": data["company"],
                "contents": data["contents"],
                "scraped_time": data["scraped_time"]
            }
        }
        docs.append(doc)

    helpers.bulk(es, docs)