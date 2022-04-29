from collections import OrderedDict
import os
import sys
import json
from typing import List
import git
from ruamel.yaml import YAML
from colorama import Fore, Style


def get_tag_kv(resourcetag, resourcetaglist):
    """
    This function returns the key,value tuple of a taglist. It helps
    indifferentiating Tag list representations like either :
    Tags:
      - Key: foo
        Value: bar

    or:

    Tags:
      foo: bar
    """
    if 'Key' in resourcetag:
        return resourcetag.get('Key'), resourcetag.get('Value')
    else:
        return resourcetag, resourcetaglist.get(resourcetag)

class Tagger:
    def __init__(self, filename: str, simulate: bool = True, setgit: bool = False):
        self.filename: str = filename
        self.resources: dict = {}
        self.stats: dict = {}
        self.obligatory_tags: dict = {}
        self.simulate = simulate
        self.git = setgit
        self.resourcetypes_to_tag: List = [
            "AWS::ApiGatewayV2::Api",
            "AWS::Athena::DataCatalog",
            "AWS::Athena::WorkGroup",
            "AWS::CertificateManager::Certificate",
            "AWS::CloudFront::Distribution",
            "AWS::CloudTrail::Trail",
            "AWS::CloudWatch::Alarm",
            "AWS::CloudWatch::AnomalyDetector",
            "AWS::Logs::LogGroup",
            "AWS::Config::ConfigRule",
            "AWS::S3::Bucket",
            "AWS::DocDB::DBCluster",
            "AWS::DocDB::DBInstance",
            "AWS::DocDB::DBSubnetGroup",
            "AWS::DynamoDB::Table",
            "AWS::DynamoDB::GlobalTable",
            "AWS::EC2::EIP",
            "AWS::EC2::EIPAssociation",
            "AWS::EC2::Instance",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::NetworkAcl",
            "AWS::EC2::NetworkAclEntry",
            "AWS::EC2::RouteTable",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::Subnet",
            "AWS::EC2::TransitGateway",
            "AWS::EC2::Volume",
            "AWS::EC2::VPC",
            "AWS::EC2::VPCEndpoint",
            "AWS::EC2::VPCEndpointService",
            "AWS::ECR::Repository",
            "AWS::EFS::FileSystem",
            "AWS::EKS::Cluster",
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            "AWS::ElasticLoadBalancingV2::Listener",
            "AWS::Events::Rule",
            "AWS::Glue::Database",
            "AWS::Glue::Crawler",
            "AWS::Glue::Job",
            "AWS::Glue::Table",
            "AWS::IAM::Policy",
            "AWS::IAM::Role",
            "AWS::Lambda::Function",
            "AWS::RDS::DBInstance",
            "AWS::Redshift::Cluster",
            "AWS::S3::Bucket",
            "AWS::SNS::Subscription",
            "AWS::SNS::Topic",
            "AWS::StepFunctions::StateMachine",
            "AWS::SSM::MaintenanceWindow",
            "AWS::SSM::Parameter",
            "AWS::SSM::PatchBaseline",
            "AWS::Synthetics::Canary",
            "AWS::WAFv2::RuleGroup",
            "AWS::WAFv2::WebACL",
        ]

        yaml = YAML()
        yaml.explicit_start = True
        yaml.preserve_quotes = True
        yaml.line_break = True
        yaml.width = 200


        try:
            with open(filename) as cfn:
                self.data = yaml.load(cfn)
        except FileNotFoundError:
            print(f"{Fore.RED}FAIL: Please provide a valid filename{Style.RESET_ALL}")
            sys.exit(1)
        except ValueError:
            print(
                f"{Fore.RED}FAIL: Please provide a filename with valid YML{Style.RESET_ALL}"
            )
            sys.exit(1)

        obligatory_tags_str = os.getenv("CFN_TAGS")
        try:
            obligatory_tags = json.loads(obligatory_tags_str)
        except json.decoder.JSONDecodeError as e:
            print(f"{Fore.RED}FAIL: malformed CFN_TAGS JSON => {e}{Style.RESET_ALL}")
            sys.exit(1)
        except TypeError:
            print(
                f"{Fore.RED}FAIL: Please set CFN_TAGS as environment variable{Style.RESET_ALL}"
            )
            sys.exit(1)
        else:
            self.resources = self.data.get("Resources")
            self.obligatory_tags = obligatory_tags


    def get_updated_tags(self, resource: str) -> List:
        try:
            return self.stats[resource]["updatedtags"]
        except KeyError:
            return []


    def get_obligatory_tags(self) -> List:
        return self.obligatory_tags


    def get_found_tags(self, resource: str) -> List:
        try:
            return self.stats[resource]["foundtags"]
        except KeyError:
            return []


    def get_added_tags(self, resource: str) -> List:
        try:
            return self.stats[resource]["addedtags"]
        except KeyError:
            return []


    def change_tags(
        self, taglist: List[OrderedDict], resource: str
    ) -> List[OrderedDict]:

        resultlist = []

        for tags in taglist:
            key, value = get_tag_kv(tags, taglist)
            self.stats[resource]["foundtags"].append(key)

            if key in self.obligatory_tags.keys():
                if value != self.obligatory_tags[key]:
                    print(
                        f"{Fore.YELLOW}    [tag][CHANGE] {key.ljust(15, ' ')} => {value} ==> {self.obligatory_tags[key]}{Style.RESET_ALL}"
                    )
                    resultlist.append(
                        OrderedDict(
                            {
                                "Key": key,
                                "Value": self.obligatory_tags[key],
                            }
                        )
                    )
                    self.stats[resource]["updatedtags"].append(key)

                else:
                    resultlist.append(OrderedDict({"Key": key, "Value": value}))
            else:
                resultlist.append(OrderedDict({"Key": key, "Value": value}))

        return resultlist

    def tag(self):
        if self.git:
            try:
                repo = git.Repo(os.getcwd())
                remote = repo.remote().url
            except git.exc.InValidGitRepositoryError:
                print("FAIL: this is no git repo, please drop the --git argument")
                sys.exit(1)

        for item in self.resources:
            restype = self.resources[item].get("Type")
            self.stats[item] = {"foundtags": [], "updatedtags": [], "addedtags": []}
            print(" ")
            print(
                f"{Fore.CYAN}[{self.filename}][Resource] {item} => {restype}{Style.RESET_ALL}"
            )
            if "Tags" in self.resources[item].get("Properties"):
                restags = self.resources[item].get("Properties").get("Tags")
                updated = self.change_tags(taglist=restags, resource=item)
                self.resources[item]["Properties"]["Tags"] = updated

            for obligtag in self.obligatory_tags.keys():
                if restype in self.resourcetypes_to_tag:
                    if obligtag not in self.stats[item]["foundtags"]:
                        # tag is not present, let's add it
                        print(
                            f"{Fore.GREEN}    [tag][   ADD] {obligtag.ljust(15, ' ')} => {self.obligatory_tags[obligtag]}{Style.RESET_ALL}"
                        )
                        self.stats[item]["addedtags"].append(obligtag)

                        addtags = OrderedDict(
                            {
                                "Key": obligtag,
                                "Value": f"{self.obligatory_tags[obligtag]}",
                            }
                        )
                        if "Tags" not in self.resources[item].get("Properties"):
                            # Resource support tags, but hasn't any
                            self.resources[item]["Properties"]["Tags"] = [addtags]

                        else:
                            self.resources[item].get("Properties").get("Tags").append(
                                addtags
                            )
            if self.git:
                gittags= OrderedDict(
                    {
                        "Key": "gitrepo",
                        "Value": remote
                    }
                )
                if "Tags" in self.resources[item].get("Properties"):
                    self.resources[item].get("Properties").get("Tags").append(
                            gittags
                    )
                else:
                    self.resources[item]["Properties"]["Tags"] = [addtags]

                gittags= OrderedDict(
                    {
                        "Key": "gitfile",
                        "Value": self.filename
                    }
                )
                self.resources[item].get("Properties").get("Tags").append(
                        gittags
                )

        yaml = YAML()
        yaml.explicit_start = True
        yaml.indent(mapping=2)
        yaml.line_break = True
        yaml.width = 200
        yaml.preserve_quotes = True
        yaml.Representer.add_representer(OrderedDict, yaml.Representer.represent_dict)

        if self.simulate:
            print(" ")
            #self.data['AWSTemplateFormatVersion'] = '2010-09-09'
            return yaml.dump(self.data, sys.stdout)
        else:
            print("Writing file...")
            with open(self.filename, "wb") as file:
                return yaml.dump(self.data, file)
