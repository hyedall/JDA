import sys
import requests
import logging
import json

def init():
    with open("elasticsearch/indices_wanted.json", "r", encoding="utf-8") as file:
        elasticsearch_url = "http://localhost:9200/wanted"
        indices_info = json.dumps(json.load(file))
        headers = {"content-type": "application/json"}
        res = requests.put(url=elasticsearch_url, data=indices_info, headers=headers)
        if res.status_code == 400:
            requests.delete(url=elasticsearch_url)
            requests.put(url=elasticsearch_url, data=indices_info, headers=headers)

    with open("kibana/kibana_export.ndjson", "r", encoding="utf-8") as file:
        kibana_url = "http://localhost:5601/api/saved_objects/_import?overwrite=true"
        headers={"kbn-xsrf": "true"}
        objects_info = {"file": file}
        requests.post(url=kibana_url, headers=headers, files=objects_info)

if __name__ == "__main__":
    if sys.argv[1] == "init":
        init()
    else:
        logging.error("InvalidArgument: Invalid arguments. (init)")