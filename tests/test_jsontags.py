import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')

cfn_template = "./tests/templates/jsontags.yml"
testcase = CfnTestTemplate(cfn_template)


def test_json_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True, setgit=True)
    cfn_tagger.tag()

    assert len(cfn_tagger.get_found_tags("ResourceWithTags")) == 1
    assert len(cfn_tagger.get_found_tags("ResourceWithJsonTags")) == 4
    assert cfn_tagger.get_added_tags("ResourceWithTags") == ['Creator']
    assert cfn_tagger.get_added_tags("ResourceWithJsonTags") == ['Creator']