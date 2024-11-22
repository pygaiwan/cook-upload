import json
import requests
from pydantic import validate_call
from pathlib import Path
from .constants import (
    NEW_PAGE_QUERY_TEMPLATE,
    NOTION_DB_API_URL,
    NOTION_PAGES_API_URL,
)
from .models import NotionDBMetadata, NotionDBSearch, NotionNewPage
from .models.notion_dbnewpage_model import SelectModel


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
        difficulty: str,
        type_: str,
        source: str,
        ingredients: str,
        steps: str,
        origin: str,
        date: str,
    ):
        params = {k: v for k, v in locals().items() if k != 'self'}
        self.is_title_used(title)
        new_query = self._create_new_page(**params)
        new_query = new_query.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )
        try:
            response = requests.post(NOTION_PAGES_API_URL, headers=self.headers, json=new_query)
            response.raise_for_status()
        except requests.HTTPError as e:
            print(e.response.json())
            (Path(__file__).parent.parent / 'errors.log').write_text(json.dumps(new_query))
            raise

    def _create_new_page(
        self,
        *,
        title: str,
        difficulty: str,
        type_: str,
        source: str,
        ingredients: str,
        steps: str,
        origin: str,
        date: str,
    ):
        model = NotionNewPage.model_validate(NEW_PAGE_QUERY_TEMPLATE)
        model.parent.database_id = self.db_id
        model.properties.name.title[0].text.content = title
        model.properties.type_.select.name = type_
        if origin:
            model.properties.origin = SelectModel.model_validate({'select': {'name': origin}})
        model.properties.difficulty.select.name = difficulty
        model.properties.source.rich_text[0].text.content = source
        if date:
            model.properties.date.date.start = date
        model.children[1].paragraph.rich_text[0].text.content = ingredients
        model.children[3].paragraph.rich_text[0].text.content = steps

        return NotionNewPage.model_validate_json(
            model.model_dump_json(by_alias=True, exclude_none=True, exclude_unset=True),
        )
