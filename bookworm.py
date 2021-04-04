from notion.client import NotionClient
import configparser
from datetime import datetime 
import pandas as pd
import numpy as np

config = configparser.ConfigParser()
config.read('notion.cfg')
cfg = config['Notion']

client = NotionClient(token_v2=cfg['token_v2'])

reading_page_block = client.get_block(cfg['reading'])

articles_id = 'b9de160a-796a-43c7-9e40-11b5e26c7392'
books_id = '0168612e-ea50-4e1c-9750-9b584270b6d0'

books = {
    'name': [],
    'identifier': [],
    'pages_read': [],
    'timestamp': []
}

timestamp = datetime.now()

# for each book or article, capture the desired data
for block in reading_page_block.children:
    if block.id not in [articles_id, books_id]:
        continue
    else:
        for row_block in block.collection.get_rows():
                books['name'].append(row_block.title)
                try:
                    books['pages_read'].append(row_block.page_number or 0)
                except AttributeError:
                    books['pages_read'].append(0) # articles don't have the pages_read property
                books['identifier'].append(row_block.id)
                books['timestamp'].append(timestamp) 

reading_list = pd.DataFrame(books)

last_snapshot = pd.read_csv('notion_reading_list.csv')

merged = reading_list.merge(
    last_snapshot, how='left', on="identifier", suffixes=("_current", "_prior")
)
merged['page_diff'] = merged['pages_read_current'] - \
    merged['pages_read_prior'].replace({np.nan: 0})
# want to log records that had progress
to_log = merged.loc[merged['page_diff']>0]

reading_log = client.get_block('b23c6a42-fdbc-4992-a6c0-8349caca6fa4')

for entry in to_log.itertuples():
    row = reading_log.collection.add_row()
    row.title = entry.name_current
    
    object_ref = client.get_block(entry.identifier)
    if object_ref.parent.parent.id == books_id:
        row.book = client.get_block(entry.identifier)
    elif object_ref.parent.parent.id == articles_id:
        row.article = client.get_block(entry.identifier)
        
    row.pages_read = entry.page_diff 
    row.timestamp = entry.timestamp_current