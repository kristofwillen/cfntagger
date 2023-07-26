#import os
import pytest

from cfntagger import Tagger
from tests.unittest import CfnTestTemplate


@pytest.fixture
def mock_envvar_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"test": "pytest"}')

# @pytest.fixture
# def mock_cfgfile_custom_tag(monkeypatch):
#     configstr="""
#     [Tags]
#     test=pytest
#     configfile=1
#     """

#     with open('./.cfntaggerrc', 'w') as configfile:
#         configfile.write(configstr)


cfn_template = "./tests/templates/nocfntags.yml"
testcase = CfnTestTemplate(cfn_template)

# def test_resources_with_cfgfile(mock_cfgfile_custom_tag):
#     cfn_tagger = Tagger(filename=cfn_template, simulate=True)
#     cfn_tagger.tag()
#     for item in testcase.get_okresources():
#         assert len(cfn_tagger.get_added_tags(item)) == 2
#         assert len(cfn_tagger.get_updated_tags(item)) == 0

#     if os.path.exists('./.cfntaggerrc'):
#         os.remove('./.cfntaggerrc')

def test_resources_with_env(mock_envvar_custom_tag):
    cfn_tagger = Tagger(filename=cfn_template, simulate=True)
    cfn_tagger.tag()
    for item in testcase.get_okresources():
        assert len(cfn_tagger.get_added_tags(item)) == 1
        assert len(cfn_tagger.get_updated_tags(item)) == 0
