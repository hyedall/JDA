from pymongo import MongoClient

def mongoLoad(**context):
    data = context['ti'].xcom_pull(task_ids='wantedJdCrawling')

    client = MongoClient(host="localhost", port=27017)
    wanted = client.JDA.wanted

    # MongoDB data insert
    wanted.insert_many([posting for posting in data["insert"]])
    # MongoDB data update
    for id in data["update"]:
        query = {"id": id}
        update = {"$set": {"validation": False}}
        wanted.update_one(query, update)
    
    print(f"Update id : {data['update'][:10]}, total : {len(data['update'])}")