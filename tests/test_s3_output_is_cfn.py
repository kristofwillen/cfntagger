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

    # s3 template has been changed, is it still valid CFN ?
    command = f"cfn-lint {template}"
    # pylint: disable=unused-variable
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    if result.stderr:
        try:
            raise subprocess.CalledProcessError(
                    returncode=result.returncode,
                    cmd=result.args,
                    stderr=result.stderr
                )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("[FAIL] Could not execute cfn-lint => " + str(e))

    else:
        # our cfntagger command changes one of our cfn templates, lets reset it
        command = f"cp {template_ok} {template}"
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )

        if result.stderr:
            try:
                raise subprocess.CalledProcessError(
                        returncode=result.returncode,
                        cmd=result.args,
                        stderr=result.stderr
                    )
            except subprocess.CalledProcessError as e:
                raise RuntimeError("[FAIL] Could not restore s3 test template => " + str(e))
