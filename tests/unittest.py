import sys
from typing import List
from ruamel.yaml import YAML


class CfnTestTemplate:
    """
    This class helps us to deal with testing Cloudformation templates.
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.resources = []
        self.okresources = []
        self.nokresources = []

        try:
            yaml = YAML()
            with open(filename, encoding='utf-8') as cfn:
                data = yaml.load(cfn)
        except FileNotFoundError:
            print(f"FAIL: Input file {self.filename} not found")
            sys.exit(1)
        except ValueError:
            print("FAIL: Please provide a filename with valid YML")
            sys.exit(1)
        else:
            self.resources = data.get("Resources")

        for res in self.resources:
            if res.startswith("Ok"):
                self.okresources.append(res)
            elif res.startswith("NOk"):
                self.nokresources.append(res)

    def get_okresources(self) -> List:
        return self.okresources

    def get_nokresources(self) -> List:
        return self.nokresources

    def get_resources(self) -> List:
        return self.resources

    def get_nr_of_resources(self) -> int:
        return len(self.resources)

    def get_nr_of_okresources(self) -> int:
        return len(self.okresources)

    def get_nr_of_nokresources(self) -> int:
        return len(self.nokresources)
