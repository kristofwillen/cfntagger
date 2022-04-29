import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')


@pytest.fixture
def mock_env_two_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof", "Team": "Devops"}')


cfn_template = "./tests/templates/ec2.yml"
testcase = CfnTestTemplate(cfn_template)


def test_found_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    for item in testcase.get_okresources():
        assert len(cfn_tagger.get_added_tags(item)) == 0
        assert len(cfn_tagger.get_updated_tags(item)) == 0

    for item in testcase.get_nokresources():
        assert (len(cfn_tagger.get_added_tags(item)) > 0 or len(cfn_tagger.get_updated_tags(item)) > 0)


def test_obligatory_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert len(cfn_tagger.get_obligatory_tags()) == 1


def test_single_added_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_added_tags("OkEC2Instance") == []
    assert cfn_tagger.get_added_tags("NOkEC2Instance") == ["Creator"]


def test_single_updated_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_updated_tags("OkEC2Instance") == []
    assert cfn_tagger.get_updated_tags("NOkEC2Instance") == []


def test_two_added_tags(mock_env_two_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_added_tags("OkEC2Instance") == ["Team"]
    assert cfn_tagger.get_added_tags("NOkEC2Instance") == ["Creator", "Team"]


def test_two_updated_tags(mock_env_two_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert cfn_tagger.get_updated_tags("OkEC2Instance") == []
    assert cfn_tagger.get_updated_tags("NOkEC2Instance") == []
