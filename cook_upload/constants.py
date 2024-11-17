from enum import Enum

NOTION_API_KEY = 'NOTION_API_KEY'
NOTION_DB_ID = 'NOTION_DB_ID'


NOTION_DB_API_URL = 'https://api.notion.com/v1/databases/{}'
NOTION_PAGES_API_URL = 'https://api.notion.com/v1/pages'

class DishDifficulty(Enum):
    easy = 'Easy'
    medium = 'Medium'
    hard = 'Hard'


NEW_PAGE_QUERY_TEMPLATE = {
    'parent': {'database_id': None},
    'properties': {
        'Name': {'title': [{'text': {'content': None}}] },
        'Type': {'select': {'name': None}},
        'Origin': {'select': {'name': None}},
        'Difficulty': {'select': {'name': None}},
        'Source': {'rich_text': [{'text': {'content': None}}]},
    },
    'children': None,
}
