# Cfntagger changes
## v0.10.3
- 20230908
- Fixes #25: AWS::Serverless::Function has map based tags (really!)
m
## v0.10.2
- 20230908
- Fixes #25: AWS::Serverless::Function has map based tags

## v10.0.1
- 20230728
- Fixes #18 : AttributeError when adding tags
- Fixes #19: don't convert existing tag formats
- Fixes #20 : don't convert tag names to lowercase

## v0.10.0
- 20230708
- Add feature request for version number #5 (configfile)
- Add feature request for version number #13 (version)
- Support for additional CloudFormation resources
- Always generate correct tag format (json/list), cfr issue #14

## v0.9.8
- 20220721
- Fix #7 where the gitfile sometimes has a wrong relative path

## v0.9.7
- 20220715
- Fix #6 where an UnboudLocalError is produced when passing -g
  with an empty CFN_TAGS

## v0.9.6
- 20220618
- Fix typo in list of resources to tag
- Improved performance

## v0.9.5
- 20220611
- Fix embarrassing bug where incorrect resources are tagged
- Add resource-tagging-support pytest
- Some Sonarqube code smells fixes
- Dont let Sonarqube scan test CFN templates

## v0.9.4
- 20220526
- fix issue with -g when not on rootdir
- fix TypeError when no Properties are defined [#2]

## v0.9.3
- 20220429
- inital release
