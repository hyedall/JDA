from datetime import datetime
from typing import Dict

class JobPosting:
    url: str
    company: str
    position: str
    contents: Dict
    scraped_time: str

    def __init__(self, url, company, position, contents):
        self.url = url
        self.company = company
        self.position = position
        self.contents = contents
        self.scraped_time = datetime.now().strftime('%Y-%m-%d')

class Config:
    MONGO_HOST = 'mongo'
    MONGO_PORT = '27017'
    MONGO_DB = 'job'
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"