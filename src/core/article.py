from datetime import datetime


class Article:
    def __init__(self, link, raw_text, date):
        self.link: str = link
        self.raw_text: str = raw_text
        self.date: datetime = date
    
    def save(self, path):
        with open(path, 'w', encoding='utf8') as f:
            f.write(self.raw_text)