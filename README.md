# cfntagger
cfntagger is a Cloudformation tagging tool. It sets tags on resources which support them in Cloudformation templates.

## Why tagging ?
Tagging resources in AWS is crucial for larger environments.  It helps you to quickly find resources based upon classifiers set in resource tags. Tag keys are often set by convention in larger teams.  So they are prone to frequent change.  And nothing is more boring than sifting through heaps of yaml files modifying tags.  Cfntagger helps you with that.


## Installation
```bash
$ pip install cfntagger
```

## Usage
```bash
$ export CFN_TAGS='{"Creator": "Erlich", "Team": "Incubator"}'
$ cfntagger -h
usage: cfntagger [-h] (--file FILE | --directory DIRECTORY) [--simulate] [--git]

Add bulk tags to CloudFormation resources

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  The CloudFormation template file to modify
  --directory DIRECTORY, -d DIRECTORY
                        A directory containing CFN templates to modify
  --simulate, -s        simulate, do not overwrite the inputfile
  --git, -g             add git remote and file info as tags
  --version, -v         show version
```

where :
* `filename` : the Cloudformation file to tag
* `directory` : a directory filled with Cloudformation templates, recursively to search
* `simulate` : whether or not to overwrite the file in place.  If specified, output the changed template to stdout. If not specified as argument (default behavior), replace the file with the corrected version.
* `addgit`: add git information, like git repo and file in which the resource has been defined

The 'file' and 'directory' arguments are mutually exclusive.

WARNING: make sure your files are committed in git before running this tool !

## Configuration
There are two ways of configuring cfntagger:

### Configfile
The configfile `.cfntaggerrc` must be present in either:
* the root of your git repo
* the current directory from where you launch cfntagger

The configfile is in ini-file format, with one section `Tags`, where tags are placed in key-value pairs:
```
[Tags]
tag1=tag1value
tag2=tag2value
````

Example:
````
[Tags]
Environment=Production
CostCenter=Sales
Application=Aviato
````

If the file `.cfntaggerrc` isn't present in one of those locations, the configuration via environment variables is used.

### Environment variables
You need to define your custom obligatory tags via the CFN_TAGS environment variable.  It must be in JSON format:
```bash
$ export CFN_TAGS='{"Creator": "Dinesh", "Team": "Devops"}'
````

This will add those tags at all resources who support tags.


## Prereqs
Have a look at the Pipfile in order to know which Python modules are required.

## Unit tests
Unit tests are provided, sample Cloudformation templates are placed in tests/templates.  Run the tests with :
```bash
$ pytest -v
````

## Reference
[Amazon documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)

