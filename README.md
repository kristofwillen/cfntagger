# cfntagger
cfntagger is a Cloudformation tagging tool.

## Usage
```bash
$ export CFN_TAGS = '{"Creator": "BCG213", "Team": "Devops"}'
$ cfntagger.py (--filename /path/to/cfn.yml | --directory /path/to/cfntemplates/) [--simulate] [--addgit]
```

where :
* `filename` : the Cloudformation file to tag
* `directory` : a directory filled with Cloudformation templates, recursively to search
* `simulate` : whether or not to overwrite the file in place.  If specified, output the changed template to stdout. If not specified as argument (default behavior), replace the file with the corrected version.
* `addgit`: add git information, like git repo and file in which the resource has been defined

The 'file' and 'directory' arguments are mutually exclusive.

WARNING: make sure your files are committed in git before running this tool !

You need to define your custom obligatory tags via the CFN_TAGS environment variable.  It must be in JSON format:
```bash
$ export CFN_TAGS = '{"Creator": "BCG213", "Team": "Devops"}'
````

This will add those tags at all resources who support tags.


## Prereqs
Have a look at the Pipfile in order to know which Python modules are required.

## Unit tests
Unit tests are provided, sample Cloudformation templates are placed in tests/templates.  Run the tests with :
```bash
$ pytest -v
````

## Todo

* Add more unit tests

## Bugs
* Some comment lines may disappear, this seems a bug in the ruamel module, cfr [bugreport #421](https://sourceforge.net/p/ruamel-yaml/tickets/421/)

