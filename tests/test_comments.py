import sys
import re
import io
import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')

cfn_template = "./tests/templates/comments.yml"
testcase = CfnTestTemplate(cfn_template)

@pytest.mark.skip(reason="waiting for upstream to fix this")
def test_comments(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)

    # capture cfntagger output to a variable
    sys.stdout = io.StringIO()
    cfn_tagger.tag()
    result = sys.stdout.getvalue()

    # restore original stdout
    sys.stdout = sys.__stdout__

    match = re.findall('# Line [1-5]', result)

    # Assume we have still some comments
    assert len(match) > 0

    # Assume each comment line is still present
    assert '# Line 1' in match
    assert '# Line 2' in match
    assert '# Line 3' in match
    assert '# Line 4' in match
    assert '# Line 5' in match
    assert '# Line 6' in match

    # Assume all comments still present
    assert len(match) == 6
