import sys
import pytest
from ruamel.yaml import YAML

class CfnTestTemplate:
    def __init__(self, filename: str):
        self.filename = filename
        self.resources = []
        self.okresources = []
        self.nokresources = []

        try:
            yaml = YAML()
            with open(filename) as cfn:
                data = yaml.load(cfn)
            #data = read_template(filename)
        except FileNotFoundError:
            print(f"FAIL: Input file {self.filename} not found")
            sys.exit(1)
        except ValueError as e:
            print("FAIL: Please provide a filename with valid YML")
            sys.exit(1)
        else:
            self.resources = data.get("Resources")

        for res in self.resources:
            if res.startswith("Ok"):
                self.okresources.append(res)
            elif res.startswith("NOk"):
                self.nokresources.append(res)

    def get_okresources(self):
        return self.okresources

    def get_nokresources(self):
        return self.nokresources

    def get_resources(self):
        return self.resources

    def get_nr_of_resources(self):
        return len(self.resources)

    def get_nr_of_okresources(self):
        return len(self.okresources)

    def get_nr_of_nokresources(self):
        return len(self.nokresources)
