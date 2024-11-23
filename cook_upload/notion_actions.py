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
        """
        Args:
            title (str): The title of the page that caused the exception.
            source (str): The source associated with the title.
            urls (list): A list of URLs where the title has already been used.
        """
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
        """
        Initializes the NotionActions instance.

        Args:
            api_key (str): The API key for authenticating with the Notion API.
            db_id (str): The ID of the Notion database to interact with.
        """
        self.api_key = api_key
        self.db_id = db_id

        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
        }

    def get_db_metadata(self) -> NotionDBMetadata:
        """
        Retrieves metadata for the Notion database.

        Returns:
            NotionDBMetadata: The metadata of the Notion database.

        Raises:
            requests.HTTPError: If the request to retrieve the metadata fails.
        """
        try:
            response = requests.get(NOTION_DB_API_URL.format(self.db_id), headers=self.headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            msg = f'Failed to get database metadata. Error {e.response.text}'
            logger.error(msg)
            raise
        return NotionDBMetadata.model_validate(response.json())

    @validate_call
    def get_entry(self, title: str = '') -> NotionDBSearch:
        """
        Retrieves an entry from the Notion database.

        Args:
            title (str, optional): The title of the page to search for. If empty, the entire database will be returned.

        Returns:
            NotionDBSearch: The search result containing the pages that match the title.
        """
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
            msg = f'Failed to get page. Error {e.response.text}'
            logger.error(msg)
            raise

        logger.debug(f'Validated page with {title} and got {response.json()}')
        return NotionDBSearch.model_validate(response.json())

    @validate_call
    def is_title_used(self, title: str, source: str, force: bool = False) -> None:
        """
        Checks if a title has already been used in the Notion database.

        Args:
            title (str): The title to check for.
            source (str): The source associated with the title.
            force (bool, optional): If True, allows the page to be added even if the title already exists.

        Raises:
            PageAlreadyCreatedError: If the title has already been used and `force` is False.
        """
        data = self.get_entry(title)
        lower_title = title.lower()
        matching_urls = [
            result.url
            for result in data.results
            for notion_title in result.properties.name.title
            if notion_title.plain_text.lower() == lower_title
        ]

        if matching_urls:
            if force:
                logger.warning(
                    f'Title {title} and {source} already added, but proceeding due to force flag.',
                )
            else:
                logger.warning(
                    f'Title {title} and {source} already added. Operation will be stopped unless force flag is used.',
                )
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
        """
        Adds a new entry to the Notion database.

        Args:
            title (str): The title of the new page.
            difficulty (str): The difficulty level of the content.
            type_ (str): The type of content.
            source (str): The source of the content.
            ingredients (str): The ingredients required.
            steps (str): The steps involved.
            origin (str): The origin of the recipe or content.
            date (str): The date for the entry.
            force (bool, optional): If True, forces adding the page.

        Raises:
            requests.HTTPError: If the request to add the new page fails.
        """
        params = {
            'title': title,
            'difficulty': difficulty,
            'type_': type_,
            'source': source,
            'ingredients': ingredients,
            'steps': steps,
            'origin': origin,
            'date': date,
        }

        self.is_title_used(title, source, force)
        new_query = self._create_new_page(**params)
        new_query = new_query.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            exclude_defaults=True,
        )

        # Not sure why model_dump does not exclude it if is not empy
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
        date: str = None,
    ):
        """
        Creates a new page model for adding to the Notion database.

        Args:
            title (str): The title of the page.
            difficulty (str): The difficulty level of the content.
            type_ (str): The type of content.
            source (str): The source of the content.
            ingredients (str): The ingredients required.
            steps (str): The steps involved.
            origin (str): The origin of the recipe or content.
            date (str): The date for the entry.

        Returns:
            NotionNewPage: The validated model of the new page to be added.
        """
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
