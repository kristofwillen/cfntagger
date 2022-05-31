import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')


cfn_template = "./tests/templates/noproperties.yml"
testcase = CfnTestTemplate(cfn_template)


def test_resources(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    for item in testcase.get_okresources():
        assert len(cfn_tagger.get_added_tags(item)) == 1
        assert len(cfn_tagger.get_updated_tags(item)) == 0


def test_found_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    assert len(cfn_tagger.get_found_tags("NOkBucket")) == 0
