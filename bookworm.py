from notion.client import NotionClient
import configparser

config = configparser.ConfigParser()
config.read('notion.cfg')
token_v2 = config['Notion']['token_v2']


client = NotionClient(token_v2=token_v2)

# Replace this URL with the URL of the page you want to edit
page = client.get_block("https://www.notion.so/myorg/Test-c0d20a71c0944985ae96e661ccc99821")

print("The old title is:", page.title)