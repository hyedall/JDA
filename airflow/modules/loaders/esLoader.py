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
    mongo = MongoClient(host="localhost", port=27017)
    es = Elasticsearch("http://localhost:9200")
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