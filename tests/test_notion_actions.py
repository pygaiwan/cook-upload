import pytest

from cook_upload import NotionActions
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
