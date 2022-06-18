from typing import List
from ruamel.yaml import YAML
from cfntagger.cfntagger import get_tag_kv


class Taglist:
    """
    This class defines some functions to return tag keys/values in testing.
    """
    def __init__(self, tagliststr):
        self.tag_keys_in_taglist = []
        self.tag_vals_in_taglist = []

        yaml = YAML()
        taglist = yaml.load(tagliststr).get('Tags')

        for tag in taglist:
            the_key, the_value = get_tag_kv(tag, taglist)
            self.tag_keys_in_taglist.append(the_key)
            self.tag_vals_in_taglist.append(the_value)


    def list_the_tag_keys(self) -> List:
        return self.tag_keys_in_taglist

    def list_the_tag_vals(self) -> List:
        return self.tag_vals_in_taglist


tagliststr1 = """\
Tags:
  - Key: tag1
    Value: foo
  - Key: tag2
    Value: bar
"""

tagliststr2 = """\
Tags:
  tag1: foo
  tag2: bar
"""

taglist1 = Taglist(tagliststr1)
taglist2 = Taglist(tagliststr2)


def test_get_tag_kv():
    assert taglist1.list_the_tag_keys() == ['tag1', 'tag2']
    assert taglist1.list_the_tag_keys() == taglist2.list_the_tag_keys()
    assert taglist1.list_the_tag_vals() == ['foo', 'bar']
    assert taglist1.list_the_tag_vals() == taglist2.list_the_tag_vals()
