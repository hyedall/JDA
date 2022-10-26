from datetime import datetime
from typing import Dict

class JobPosting:
    url: str
    company: str
    position: str
    contents: Dict
    scraped_time: str

    def __init__(self, url, company, position, contents, scraped_time=datetime.now().strftime('%Y-%m-%d')):
        self.url = url
        self.company = company
        self.position = position
        self.contents = contents
        self.scraped_time = scraped_time