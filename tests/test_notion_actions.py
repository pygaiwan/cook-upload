import pytest

from cook_upload import DishDifficulty, NotionActions, TitleAlreadyUsedError
from cook_upload.models import NotionDBMetadata


class Test_NotionActions:
    @pytest.mark.vcr
    def test_get_db_data(self, notion: NotionActions):
        data = notion.get_db_metadata()
        assert isinstance(data, NotionDBMetadata)

    @pytest.mark.vcr
    def test_query_db_same_title(self, notion: NotionActions):
        assert len(notion.get_entry(title='Baklava').results) == 1

    @pytest.mark.vcr
    def test_query_db_title_not_found(self, notion: NotionActions):
        assert len(notion.get_entry(title='Unknwon dish').results) == 0

    @pytest.mark.vcr
    def test_query_db_without_title(self, notion: NotionActions):
        assert len(notion.get_entry().results) > 0

    @pytest.mark.vcr
    def test_is_title_already_used(self, notion: NotionActions):
        with pytest.raises(
            TitleAlreadyUsedError,
            match='The title "Baklava" has already been used. See: https://www.notion.so/Baklava-d4251acfeb2d4f659809543ca7524094',
        ):
            notion.is_title_used(title='Baklava')

    @pytest.mark.vcr
    def test_is_title_used_not_used(self, notion: NotionActions):
        assert notion.is_title_used(title='Moise') is None

    def test_new_page_payload_check(self, notion: NotionActions):
        expected = {
            'parent': {'database_id': '56dada1e4604428b9e2d7d1a8d2ad131'},
            'properties': {
                'Name': {'title': [{'text': {'content': 'Moise'}}]},
                'Type': {'select': {'name': 'Sweet'}},
                'Origin': {'select': {'name': 'Korea'}},
                'Difficulty': {'select': {'name': 'Hard'}},
                'Source': {'rich_text': [{'text': {'content': 'Test'}}]},
            },
        }
        data = notion._create_new_page(
            title='Moise',
            type_='Sweet',
            origin='Korea',
            difficulty='Hard',
            source='Test',
        )
        assert data.model_dump(by_alias=True, exclude_none=True) == expected

    def test_new_page_payload_check_without_origin(self, notion: NotionActions):
        expected = {
            'parent': {'database_id': '56dada1e4604428b9e2d7d1a8d2ad131'},
            'properties': {
                'Name': {'title': [{'text': {'content': 'Moise'}}]},
                'Type': {'select': {'name': 'Sweet'}},
                'Difficulty': {'select': {'name': 'Hard'}},
                'Source': {'rich_text': [{'text': {'content': 'Test'}}]},
            },
        }
        data = notion._create_new_page(
            title='Moise',
            type_='Sweet',
            difficulty='Hard',
            source='Test',
        )
        assert data.model_dump(by_alias=True, exclude_none=True) == expected

    def test_add_entry_without_origin(self, notion: NotionActions):
        notion.add_entry(
            title='Moise', difficulty=DishDifficulty.easy, type_='Meat', steps='', source='asd',
        )
