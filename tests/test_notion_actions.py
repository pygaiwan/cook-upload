import pytest

from cook_upload import NotionActions, TitleAlreadyUsedError
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

    # def test_add_entry(self, notion: NotionActions):
    #     notion.add_entry({'title': 'Moise'})
