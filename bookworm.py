from notion.client import NotionClient
import configparser
from datetime import datetime 
import pandas as pd

config = configparser.ConfigParser()
config.read('notion.cfg')
cfg = config['Notion']

client = NotionClient(token_v2=cfg['token_v2'])

reading = client.get_block(cfg['reading'])

articles_id = 'b9de160a-796a-43c7-9e40-11b5e26c7392'
books_id = '0168612e-ea50-4e1c-9750-9b584270b6d0'

articles = {
    'names': [],
    'links': [],
    'timestamps': []
}
books = {
    'names': [],
    'links': [],
    'pages_read': [],
    'timestamps': []
}

timestamp = datetime.now()
# for each book or article, capture the name
for block in reading.children:
    if block.id not in [articles_id, books_id]:
        continue
    elif block.id == articles_id:
        for row_block in block.collection.get_rows():
            articles['names'].append(row_block.title)
            articles['links'].append(row_block.id)
            articles['timestamps'].append(timestamp)
    elif block.id == books_id:
        for row_block in block.collection.get_rows():
            books['names'].append(row_block.title)
            books['pages_read'].append(row_block.page_number)
            books['links'].append(row_block.id)
            books['timestamps'].append(timestamp) 
            
