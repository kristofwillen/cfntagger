import subprocess
import pytest
from cfntagger import Tagger

template = "./tests/templates/s3.yml"
template_ok = "./tests/templates/s3-Ok.yml"


@pytest.fixture
def mock_env_single_custom_tag(monkeypatch):
    monkeypatch.setenv("CFN_TAGS", '{"Creator": "kristof"}')


def test_found_tags(mock_env_single_custom_tag):
    # Run cfntagger on s3 template
    cfn_tagger = Tagger(filename=template, simulate=False)
    cfn_tagger.tag()

    try:
        # s3 template has been changed, is it still valid CFN ?
        command = f"cfn-lint {template}"
        # pylint: disable=unused-variable
        output = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )

    except Exception as e:
        raise Exception("[FAIL] Could not execute cfn-lint => " + str(e))

    else:
        # our cfntagger command changes one of our cfn templates, lets reset it
        command = f"cp {template_ok} {template}"
        try:
            output = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, universal_newlines=True
            )

        except Exception as e:
            raise Exception("[FAIL] Could not execute git restore => " + str(e))
