import subprocess
import json

from cfntagger import Tagger

cfn_template = "./tests/templates/ec2.yml"
cfn_tagger = Tagger(filename=cfn_template, simulate=True)

resource_template = "/tmp/foo.yml"


def test_resource_supports_tags():
    for resource in cfn_tagger.resourcetypes_to_tag:
        cfn_file_contents=f"""---
AWSTemplateFormatVersion: 2010-09-09
Description: verify if resource supports tags

Resources:
  MyFoo:
    Type: {resource}
    Properties:
      Tags:
        - Key: foo
          Value: bar

        """

        with open(resource_template, 'w', encoding='utf-8') as cfnt:
            cfnt.write(cfn_file_contents)


        command = f"cfn-lint {resource_template} --format json"
        output = subprocess.run(
            command, shell=True, universal_newlines=True, capture_output=True
        )


        try:
            result = json.loads(output.stdout)
        except json.JSONDecodeError:
            print('Failure in cfn-lint output')
            assert True is False
        else:
            for failure in result:
                # we dont want to see cfn-lint failures on E3002
                if failure['Message'].endswith('Properties/Tags'):
                    assert failure['Rule']['Id'] != 'E3002'
