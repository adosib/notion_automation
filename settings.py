from notion.client import NotionClient
import configparser
from pathlib import Path
from logger import NotionClientWithLogger # DELETE

ARTICLES_ID = 'b9de160a-796a-43c7-9e40-11b5e26c7392'
BOOKS_ID = '0168612e-ea50-4e1c-9750-9b584270b6d0'
READING_LOG_ID = 'b23c6a42-fdbc-4992-a6c0-8349caca6fa4'
LAST_SNAPSHOT = Path(__file__).parent.absolute() / 'notion_reading_list.csv'
    
config = configparser.ConfigParser()
config.read('notion.cfg')
cfg = config['Notion']

client = NotionClient(token_v2=cfg['token_v2'])
