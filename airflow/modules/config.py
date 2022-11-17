import os
from datetime import datetime

class JobPosting:
    id: str
    url: str
    company: str
    position: str
    contents: dict
    validation: bool
    scraped_time: str

    def __init__(self, id, url, company, position, contents):
        self.id = id
        self.url = url
        self.company = company
        self.position = position
        self.contents = contents
        self.validation = True
        self.scraped_time = datetime.now().strftime('%Y-%m-%d')
        
try:
    MONGO_HOST = os.environ["MONGO_HOST"]
except:
    MONGO_HOST = "localhost"
try:
    MONGO_PORT = int(os.environ["MONGO_PORT"])
except:
    MONGO_PORT = 27017
try:
    ELASTICSEARCH_HOST = os.environ["ELASTICSEARCH_HOST"]
except:
    ELASTICSEARCH_HOST = "localhost"
try:
    ELASTICSEARCH_PORT = os.environ["ELASTICSEARCH_PORT"]
except:
    ELASTICSEARCH_PORT = 9200