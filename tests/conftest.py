import os

import pytest

from cook_upload import NotionActions
from cook_upload.constants import NOTION_API_KEY, NOTION_DB_ID, OPENAI_API_KEY, OPENAI_PROJECT_ID
from cook_upload.openai_actions import OpenAIActions


@pytest.fixture(scope='session')
def vcr_config():
    return {
        'filter_headers': [('Authorization', 'dummy')],
    }


@pytest.fixture
def notion() -> NotionActions:
    return NotionActions(os.getenv(NOTION_API_KEY), os.getenv(NOTION_DB_ID))


@pytest.fixture
def openai() -> OpenAIActions:
    return OpenAIActions(os.getenv(OPENAI_API_KEY), os.getenv(OPENAI_PROJECT_ID))
