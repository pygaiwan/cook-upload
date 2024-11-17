from copy import deepcopy

import requests
from pydantic import validate_call

from .constants import (
    NEW_PAGE_QUERY_TEMPLATE,
    NOTION_DB_API_URL,
    NOTION_PAGES_API_URL,
    DishDifficulty,
)
from .models import NotionDBMetadata, NotionDBSearch, NotionNewPage


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

    @validate_call
    def add_entry(
        self,
        title: str,
        difficulty: DishDifficulty,
        type_: str,
        source: str,
        steps: str,
        origin: str = None,
    ):
        self.is_title_used(title)
        new_query = self._create_new_page(
            title=title, type_=type_, difficulty=difficulty.value, source=source, origin=origin,
        )
        response = requests.post(
            NOTION_PAGES_API_URL,
            headers=self.headers,
            json=new_query.model_dump(by_alias=True, exclude_none=True),
        )
        response.raise_for_status()

    def _create_new_page(self, *, title, type_, difficulty, source, origin=None):
        data = deepcopy(NEW_PAGE_QUERY_TEMPLATE)
        data['parent']['database_id'] = self.db_id
        data['properties']['Name']['title'][0]['text']['content'] = title
        data['properties']['Type']['select']['name'] = type_
        if origin:
            data['properties']['Origin']['select']['name'] = origin
        else:
            del data['properties']['Origin']
        data['properties']['Difficulty']['select']['name'] = difficulty
        data['properties']['Source']['rich_text'][0]['text']['content'] = source

        return NotionNewPage.model_validate(data)
