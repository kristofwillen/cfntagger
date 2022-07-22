import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')

cfn_template = "./tests/templates/ec2.yml"
testcase = CfnTestTemplate(cfn_template)


def test_git_tags(mock_env_single_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True, setgit=True)
    cfn_tagger.tag()

    assert len(cfn_tagger.get_git_tags(cfn_template)) == 2
    assert './' + cfn_tagger.get_git_tags(cfn_template)['gitfile'] == cfn_template

    repo_git = cfn_tagger.get_git_tags(cfn_template)['gitrepo'].lower()
    if repo_git.endswith('.git'):
        assert repo_git == "https://github.com/kristofwillen/cfntagger.git"
    else:
        assert repo_git == "https://github.com/kristofwillen/cfntagger"
