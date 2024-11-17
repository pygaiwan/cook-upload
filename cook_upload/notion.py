import requests
from pydantic import validate_call

from .constants import NOTION_DB_API_URL, DishDifficulty
from .models import NotionDBMetadata, NotionDBSearch


class TitleAlreadyUsedError(Exception):
    """Exception raised when a title has already been used."""

    def __init__(self, title: str, urls: list):
        self.title = title
        self.urls = urls or []
        super().__init__(self.__str__())

    def __str__(self):
        urls = [str(url) for url in self.urls]
        return f'The title "{self.title}" has already been used. See: {", ".join(urls)}'


class NotionActions:
    def __init__(self, api_key, db_id):
        self.api_key = api_key
        self.db_id = db_id

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        }

    @validate_call
    def get_db_metadata(self) -> NotionDBMetadata:
        response = requests.get(NOTION_DB_API_URL.format(self.db_id), headers=self.headers)
        return NotionDBMetadata.model_validate(response.json())

    @validate_call
    def get_entry(self, title: str = '') -> NotionDBSearch:
        """Notion will return the whole db if title is an empty string"""
        data = {'filter': {'property': 'Name', 'title': {'equals': title}}}
        response = requests.post(
            f'{NOTION_DB_API_URL.format(self.db_id)}/query',
            headers=self.headers,
            json=data,
        )
        return NotionDBSearch.model_validate(response.json())

    @validate_call
    def is_title_used(self, title: str) -> None:
        data = self.get_entry(title)
        lower_title = title.lower()
        matching_urls = [
            result.url
            for result in data.results
            for notion_title in result.properties.name.title
            if notion_title.plain_text.lower() == lower_title
        ]

        if matching_urls:
            raise TitleAlreadyUsedError(title, matching_urls)

    def add_entry(
        self,
        title: str,
        difficulty: DishDifficulty,
        type_: str,
        source: str,
        steps: str,
        origin: str = None,
    ):
        try:
            self.is_title_used(title)
        except TitleAlreadyUsedError as e:
            print(e)
            raise
