from enum import Enum

NOTION_API_KEY = 'NOTION_API_KEY'
NOTION_DB_ID = 'NOTION_DB_ID'


NOTION_DB_API_URL = 'https://api.notion.com/v1/databases/{}'
NOTION_PAGES_API_URL = 'https://api.notion.com/v1/pages'

OPENAI_API_KEY = 'OPENAI_API_KEY'
OPENAI_PROJECT_ID = 'OPENAI_PROJECT_ID'


class DishDifficulty(str, Enum):
    easy = 'Easy'
    medium = 'Medium'
    hard = 'Hard'


NEW_PAGE_QUERY_TEMPLATE = {
    'parent': {'database_id': ''},
    'properties': {
        'Name': {'title': [{'text': {'content': ''}}]},
        'Type': {'select': {'name': ''}},
        'Origin': None,
        'Difficulty': {'select': {'name': ''}},
        'Source': {'rich_text': [{'text': {'content': ''}}]},
        'Date': {'date': {'start': None}},
    },
    'children': [],
}

DELIMITER = {'object': 'block', 'type': 'divider', 'divider': {}}

OPENAI_TEXT = """The attached image is a receipt for a dish. Extract the title, the steps and the
ingredients and return them, exactly as they are in the model provided.
Do not change or translate the text.
Use bullet points for the ingredients and numbered list for the steps. It is important that this list format is maintained."""

OPENAI_MESSAGE = {
    'role': 'user',
    'content': [
        {'type': 'text', 'text': OPENAI_TEXT},
        {
            'type': 'image_url',
            'image_url': {'url': None},
        },
    ],
}


DATETIME_STR = '%Y%m%d'
DATETIME_FORMATTED = '%Y-%m-%d'
