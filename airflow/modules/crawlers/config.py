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