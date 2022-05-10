import pytest

from cfntagger import Tagger


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')


@pytest.fixture
def mock_env_two_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof", "Team": "Devops"}')


cfn_template = "./tests/templates/s3.yml"


def test_found_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert len(cfn_tagger.get_found_tags("MyBucket")) == 3
    assert len(cfn_tagger.get_found_tags("AnotherBucket")) == 3
    assert len(cfn_tagger.get_found_tags("BucketWithoutTags")) == 0
    assert len(cfn_tagger.get_found_tags("BucketWithSpecialTags")) == 3


def test_obligatory_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert len(cfn_tagger.get_obligatory_tags()) == 1


def test_single_added_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_added_tags("MyBucket") == []
    assert cfn_tagger.get_added_tags("AnotherBucket") == ["Creator"]
    assert cfn_tagger.get_added_tags("BucketWithoutTags") == ["Creator"]
    assert cfn_tagger.get_added_tags("BucketWithSpecialTags") == ["Creator"]


def test_single_updated_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_updated_tags("MyBucket") == []
    assert cfn_tagger.get_updated_tags("AnotherBucket") == []
    assert cfn_tagger.get_updated_tags("BucketWithoutTags") == []
    assert cfn_tagger.get_updated_tags("BucketWithSpecialTags") == []


def test_two_added_tags(mock_env_two_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_added_tags("MyBucket") == []
    assert cfn_tagger.get_added_tags("AnotherBucket") == ["Creator"]
    assert cfn_tagger.get_added_tags("BucketWithoutTags") == ["Creator", "Team"]


def test_two_updated_tags(mock_env_two_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_updated_tags("MyBucket") == ["Team"]
    assert cfn_tagger.get_updated_tags("AnotherBucket") == []
    assert cfn_tagger.get_updated_tags("BucketWithoutTags") == []
