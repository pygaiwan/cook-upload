import pytest

from cook_upload import (
    DishDifficulty,
    NotionActions,
    NotionDBMetadata,
    PageAlreadyCreatedError,
)


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
            PageAlreadyCreatedError,
            match='Title "Baklava" with source "Lebanon Cookbookp pg 413" has already been used. See: https://www.notion.so/Baklava-d4251acfeb2d4f659809543ca7524094',
        ):
            notion.is_title_used(title='Baklava', source='Lebanon Cookbookp pg 413')

    @pytest.mark.vcr
    def test_is_title_used_not_used(self, notion: NotionActions):
        assert notion.is_title_used(title='Moise', source='moise') is None

    @pytest.mark.vcr
    def test_new_page_payload_check(self, notion: NotionActions):
        expected = {
            'children': [
                {
                    'heading_2': {
                        'rich_text': [{'text': {'content': 'Ingredients'}, 'type': 'text'}],
                    },
                    'object': 'block',
                    'type': 'heading_2',
                },
                {
                    'object': 'block',
                    'paragraph': {'rich_text': [{'text': {'content': 'a,b,c'}, 'type': 'text'}]},
                    'type': 'paragraph',
                },
                {
                    'heading_2': {'rich_text': [{'text': {'content': 'Steps'}, 'type': 'text'}]},
                    'object': 'block',
                    'type': 'heading_2',
                },
                {
                    'object': 'block',
                    'paragraph': {'rich_text': [{'text': {'content': 'a,b,c'}, 'type': 'text'}]},
                    'type': 'paragraph',
                },
            ],
            'parent': {'database_id': '56dada1e4604428b9e2d7d1a8d2ad131'},
            'properties': {
                'Date': {'date': {'start': '2024-12-21'}},
                'Difficulty': {'select': {'name': 'Hard'}},
                'Name': {'title': [{'text': {'content': 'Moise'}}]},
                'Origin': {'select': {'name': 'Korea'}},
                'Source': {'rich_text': [{'text': {'content': 'Test'}}]},
                'Type': {'select': {'name': 'Sweet'}},
            },
        }
        data = notion._create_new_page(
            title='Moise',
            type_='Sweet',
            origin='Korea',
            difficulty='Hard',
            source='Test',
            ingredients='a,b,c',
            steps='a,b,c',
            date='2024-12-21',
        )
        assert data.model_dump(by_alias=True, exclude_none=True) == expected
    
    @pytest.mark.vcr
    def test_new_page_payload_check_without_origin(self, notion: NotionActions):
        expected = {
            'children': [
                {
                    'heading_2': {
                        'rich_text': [{'text': {'content': 'Ingredients'}, 'type': 'text'}],
                    },
                    'object': 'block',
                    'type': 'heading_2',
                },
                {
                    'object': 'block',
                    'paragraph': {'rich_text': [{'text': {'content': 'a,b,c'}, 'type': 'text'}]},
                    'type': 'paragraph',
                },
                {
                    'heading_2': {'rich_text': [{'text': {'content': 'Steps'}, 'type': 'text'}]},
                    'object': 'block',
                    'type': 'heading_2',
                },
                {
                    'object': 'block',
                    'paragraph': {'rich_text': [{'text': {'content': 'a,b,c'}, 'type': 'text'}]},
                    'type': 'paragraph',
                },
            ],
            'parent': {'database_id': '56dada1e4604428b9e2d7d1a8d2ad131'},
            'properties': {
                'Date': {'date': {'start': '2024-12-21'}},
                'Difficulty': {'select': {'name': 'Hard'}},
                'Name': {'title': [{'text': {'content': 'Moise'}}]},
                'Source': {'rich_text': [{'text': {'content': 'Test'}}]},
                'Type': {'select': {'name': 'Sweet'}},
            },
        }

        data = notion._create_new_page(
            title='Moise',
            type_='Sweet',
            difficulty='Hard',
            ingredients='a,b,c',
            steps='a,b,c',
            date='2024-12-21',
            source='Test',
            origin=None,
        )
        assert data.model_dump(by_alias=True, exclude_none=True) == expected

    @pytest.mark.vcr
    def test_add_entry_without_origin(self, notion: NotionActions):
        notion.add_entry(
            title='Moise',
            difficulty=DishDifficulty.easy,
            type_='Meat',
            steps='',
            source='asd',
            ingredients='a,b,c',
            date='2024-12-21',
            origin=None,
        )
        assert len(notion.get_entry(title='Moise').results) == 1

    @pytest.mark.vcr
    def test_dish_type(self, notion: NotionActions):
        data = notion.dish_type
        to_be_found = ['pasta', 'dough', 'poultry', 'meat', 'pancakes']

        assert all(x in data for x in to_be_found)
