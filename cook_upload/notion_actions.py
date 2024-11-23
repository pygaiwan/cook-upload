import requests
from pydantic import validate_call
from requests.models import HTTPError

from .constants import (
    NEW_PAGE_QUERY_TEMPLATE,
    NOTION_DB_API_URL,
    NOTION_PAGES_API_URL,
)
from .logger import logger
from .models import NotionDBMetadata, NotionDBSearch, NotionNewPage
from .models.notion_dbnewpage_model import SelectModel


class PageAlreadyCreatedError(Exception):
    """Exception raised when a title has already been used."""

    def __init__(self, title: str, source: str, urls: list):
        self.title = title
        self.urls = urls or []
        self.source = source
        super().__init__(self.__str__())

    def __str__(self):
        urls = ', '.join(str(url) for url in self.urls)
        msg = f'Title "{self.title}" with source "{self.source}" has already been used. See: {urls}'
        return msg


class NotionActions:
    def __init__(self, api_key, db_id):
        self.api_key = api_key
        self.db_id = db_id

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        }

    def get_db_metadata(self) -> NotionDBMetadata:
        response = requests.get(NOTION_DB_API_URL.format(self.db_id), headers=self.headers)
        return NotionDBMetadata.model_validate(response.json())

    @validate_call
    def get_entry(self, title: str = '') -> NotionDBSearch:
        """Notion will return the whole db if title is an empty string"""
        data = {'filter': {'property': 'Name', 'title': {'equals': title}}}
        logger.info(f'Getting page with title {title}')
        try:
            response = requests.post(
                f'{NOTION_DB_API_URL.format(self.db_id)}/query',
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
        except HTTPError as e:
            msg = f'Failed to get page. Error {e}'
            logger.error(msg)
            raise e

        logger.debug(f'Validated page with {title} and got {response.json()}')
        return NotionDBSearch.model_validate(response.json())

    @validate_call
    def is_title_used(self, title: str, source: str, force: bool = False) -> None:
        data = self.get_entry(title)
        lower_title = title.lower()
        matching_urls = [
            result.url
            for result in data.results
            for notion_title in result.properties.name.title
            if notion_title.plain_text.lower() == lower_title
        ]

        if matching_urls:
            logger.warning(
                f'Title {title} and {source} already added. If -f is used, the page will be added.',
            )

            if not force:
                urls = ', '.join(str(url) for url in matching_urls)
                msg = f'Title "{title}" with source "{source}" has already been used. See: {urls}'
                logger.error(msg)
                raise PageAlreadyCreatedError(title, source, matching_urls)

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
        force: bool = False,
    ):
        params = {k: v for k, v in locals().items() if k not in ('self', 'force')}
        self.is_title_used(title, source, force)
        new_query = self._create_new_page(**params)
        new_query = new_query.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )

        if not date:
            del new_query['properties']['Date']
        try:
            logger.info(f'Trying adding a new page with query {new_query}')
            response = requests.post(NOTION_PAGES_API_URL, headers=self.headers, json=new_query)
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(
                f'Error in creating a new page with query: {new_query} Error {e.response.json()}',
            )
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
