import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Environment": "Development"}')

cfn_template = "./tests/templates/jsontags.yml"
testcase = CfnTestTemplate(cfn_template)


def test_json_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True, setgit=True)
    cfn_tagger.tag()

    assert len(cfn_tagger.get_found_tags("ResourceWithTags")) == 1
    assert len(cfn_tagger.get_added_tags("ResourceWithTags")) == 1
    assert len(cfn_tagger.get_updated_tags("ResourceWithTags")) == 0
    assert cfn_tagger.get_added_tags("ResourceWithTags") == ['Environment']

    assert len(cfn_tagger.get_found_tags("ResourceWithoutTags")) == 0
    assert len(cfn_tagger.get_added_tags("ResourceWithoutTags")) == 1
    assert len(cfn_tagger.get_updated_tags("ResourceWithoutTags")) == 0
    assert cfn_tagger.get_added_tags("ResourceWithoutTags") == ['Environment']

    assert len(cfn_tagger.get_found_tags("ResourceWithoutJsonTags")) == 0
    assert len(cfn_tagger.get_added_tags("ResourceWithoutJsonTags")) == 1
    assert len(cfn_tagger.get_updated_tags("ResourceWithoutJsonTags")) == 0
    assert cfn_tagger.get_added_tags("ResourceWithoutJsonTags") == ['Environment']

    assert len(cfn_tagger.get_found_tags("ResourceWithJsonTags")) == 4
    assert len(cfn_tagger.get_added_tags("ResourceWithJsonTags")) == 0
    assert len(cfn_tagger.get_updated_tags("ResourceWithJsonTags")) == 1
    assert cfn_tagger.get_updated_tags("ResourceWithJsonTags") == ['Environment']
