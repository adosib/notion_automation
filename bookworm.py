from notion.client import NotionClient
import configparser

config = configparser.ConfigParser()
config.read('notion.cfg')
cfg = config['Notion']


client = NotionClient(token_v2=cfg['token_v2'])

reading = client.get_block(cfg['reading_assignments'])

for row_block in reading.collection.get_rows():
    print(row_block.title, row_block.page_number)