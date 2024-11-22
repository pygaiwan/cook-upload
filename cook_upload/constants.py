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
    'children': [
        {
            'object': 'block',
            'type': 'heading_2',
            'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': 'Ingredients'}}]},
        },
        {
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': None}}]},
        },
        {
            'object': 'block',
            'type': 'heading_2',
            'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': 'Steps'}}]},
        },
        {
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': None}}]},
        },
    ],
}

OPENAI_TEXT = """The attached image is a receipt for a dish. Extract the title, the steps and the
ingredients and return them, exactly as they are in the model provided.
Do not change or translate the text. """

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
