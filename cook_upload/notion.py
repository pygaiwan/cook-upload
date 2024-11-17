import requests
from pydantic import validate_call

from .constants import NOTION_DB_API_URL
from .models import NotionDBMetadata, NotionDBSearch


class NotionActions:
    def __init__(self, api_key, db_id):
        self.api_key = api_key
        self.db_id = db_id

        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Notion-Version': '2022-06-28'}

    @validate_call
    def get_db_metadata(self) -> NotionDBMetadata:
        response = requests.get(NOTION_DB_API_URL.format(self.db_id), headers=self.headers)
        return NotionDBMetadata.model_validate(response.json())

    @validate_call
    def get_entry(self, title: str | None = None) -> NotionDBSearch:
        data = {'filter': {'property': 'Name', 'title': {'equals': title}}}
        response = requests.post(
            f'{NOTION_DB_API_URL.format(self.db_id)}/query',
            headers=self.headers | {'Content-Type': 'application/json'},
            json=data,
        )

        return NotionDBSearch.model_validate(response.json())
