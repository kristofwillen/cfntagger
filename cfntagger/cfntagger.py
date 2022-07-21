from collections import OrderedDict
import os
import re
import sys
import json
from typing import List, Dict
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
    """
    Main class for cfntagger
    """
    def __init__(self, filename: str, simulate: bool = True, setgit: bool = False):
        self.filename: str = filename
        self.resources: dict = {}
        self.stats: dict = {}
        self.obligatory_tags: dict = {}
        self.simulate = simulate
        self.git = setgit
        self.has_properties = True
        self.resourcetypes_to_tag: List = [
            "AWS::AccessAnalyzer::Analyzer",
            "AWS::ApiGatewayV2::Api",
            "AWS::AppStream::Fleet",
            "AWS::AppStream::ImageBuilder",
            "AWS::AppStream::Stack",
            "AWS::AppSync::GraphQLApi",
            "AWS::Athena::DataCatalog",
            "AWS::Athena::WorkGroup",
            "AWS::CertificateManager::Certificate",
            "AWS::Cloud9::Environment",
            "AWS::CloudFront::Distribution",
            "AWS::CloudTrail::Trail",
            "AWS::CodeBuild::Project",
            "AWS::CodeArtifact::Domain",
            "AWS::CodeArtifact::Repository",
            "AWS::CodeCommit::Repository",
            "AWS::CodeDeploy::Application",
            "AWS::CodeGuruReviewer::RepositoryAssociation",
            "AWS::CodePipeline::CustomActionType",
            "AWS::CodePipeline::Pipeline",
            "AWS::DataBrew::Dataset",
            "AWS::DataBrew::Job",
            "AWS::DataBrew::Project",
            "AWS::DataBrew::Recipe",
            "AWS::DataBrew::Schedule",
            "AWS::DocDB::DBCluster",
            "AWS::DocDB::DBInstance",
            "AWS::DocDB::DBSubnetGroup",
            "AWS::DynamoDB::Table",
            "AWS::EC2::EIP",
            "AWS::EC2::Instance",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::NetworkAcl",
            "AWS::EC2::RouteTable",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::Subnet",
            "AWS::EC2::TransitGateway",
            "AWS::EC2::Volume",
            "AWS::EC2::VPC",
            "AWS::ECR::Repository",
            "AWS::ECS::Cluster",
            "AWS::ECS::ContainerInstance",
            "AWS::ECS::Service",
            "AWS::ECS::Task",
            "AWS::ECS::TaskDefinition",
            "AWS::EKS::Cluster",
            "AWS::EKS::Addon",
            "AWS::EKS::NodeGroup",
            "AWS::EKS::FargateProfile",
            "AWS::ElasticBeanstalk::Environment",
            "AWS::EMR::Cluster",
            "AWS::EMR::Studio",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ParameterGroup",
            "AWS::ElastiCache::SecurityGroup",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::ElastiCache::SubnetGroup",
            "AWS::ElastiCache::Snapshot",
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            "AWS::ElasticSearch::Domain",
            "AWS::Events::EventBus",
            "AWS::FMS::Policy",
            "AWS::FSx::FileSystem",
            "AWS::Glue::Crawler",
            "AWS::Glue::DevEndpoint",
            "AWS::Glue::MLTransform",
            "AWS::Glue::Job",
            "AWS::Glue::Registry",
            "AWS::Glue::Schema",
            "AWS::Glue::Trigger",
            "AWS::Glue::Workflow",
            "AWS::IAM::Role",
            "AWS::IAM::OIDCProvider",
            "AWS::IAM::SAMLProvider",
            "AWS::IAM::ServerCertificate",
            "AWS::IAM::User",
            "AWS::IAM::VirtualMFADevice",
            "AWS::ImageBuilder::Component",
            "AWS::ImageBuilder::ContainerRecipe",
            "AWS::ImageBuilder::DistributionConfiguration",
            "AWS::ImageBuilder::Image",
            "AWS::ImageBuilder::ImagePipeline",
            "AWS::ImageBuilder::ImageRecipe",
            "AWS::ImageBuilder::InfrastructureConfiguration",
            "AWS::KMS::Key",
            "AWS::KMS::ReplicaKey",
            "AWS::Kinesis::Stream",
            "AWS::KinesisAnalyticsV2::Application",
            "AWS::KinesisFirehose::DeliveryStream",
            "AWS::Lambda::Function",
            "AWS::Lightsail::Bucket",
            "AWS::Lightsail::Certificate",
            "AWS::Lightsail::Container",
            "AWS::Lightsail::Database",
            "AWS::Lightsail::Disk",
            "AWS::Lightsail::Distribution",
            "AWS::Lightsail::Instance",
            "AWS::Lightsail::LoadBalancer",
            "AWS::Logs::LogGroup",
            "AWS::AmazonMQ::Broker",
            "AWS::AmazonMQ::Configuration",
            "AWS::MemoryDB::User",
            "AWS::MemoryDB::ACL",
            "AWS::MemoryDB::Cluster",
            "AWS::MemoryDB::ParameterGroup",
            "AWS::MemoryDB::SubnetGroup",
            "AWS::MWAA::Environment",
            "AWS::Neptune::DBSubnetGroup",
            "AWS::Neptune::DBCluster",
            "AWS::Neptune::DBClusterParameterGroup",
            "AWS::Neptune::DBInstance",
            "AWS::Neptune::DBParameterGroup",
            "AWS::NetworkFirewall::RuleGroup",
            "AWS::NetworkFirewall::Firewall",
            "AWS::NetworkFirewall::FirewallPolicy",
            "AWS::NetworkManager::ConnectAttachment",
            "AWS::NetworkManager::ConnectPeer",
            "AWS::NetworkManager::CoreNetwork",
            "AWS::NetworkManager::Device",
            "AWS::NetworkManager::GlobalNetwork",
            "AWS::NetworkManager::Link",
            "AWS::NetworkManager::Site",
            "AWS::NetworkManager::SiteToSiteVpnAttachment",
            "AWS::NetworkManager::VpcAttachment",
            "AWS::OpenSearchService::Domain",
            "AWS::QuickSight::Theme",
            "AWS::QuickSight::Analysis",
            "AWS::QuickSight::Dashboard",
            "AWS::QuickSight::DataSet",
            "AWS::QuickSight::DataSource",
            "AWS::QuickSight::Template",
            "AWS::RDS::DBInstance",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBClusterParameterGroup",
            "AWS::RDS::DBParameterGroup",
            "AWS::RDS::DBProxy",
            "AWS::RDS::DBProxyEndpoint",
            "AWS::RDS::DBSecurityGroup",
            "AWS::RDS::DBSubnetGroup",
            "AWS::RDS::OptionGroup",
            "AWS::Redshift::Cluster",
            "AWS::Redshift::ClusterParameterGroup",
            "AWS::Redshift::ClusterSecurityGroup",
            "AWS::Redshift::ClusterSubnetGroup",
            "AWS::Redshift::EventSubscription",
            "AWS::Route53Resolver::FirewallDomainList",
            "AWS::Route53Resolver::FirewallRuleGroup",
            "AWS::Route53Resolver::FirewallRuleGroupAssociation",
            "AWS::Route53Resolver::ResolverEndpoint",
            "AWS::Route53Resolver::ResolverRule",
            "AWS::S3::Bucket",
            "AWS::S3::StorageLens",
            "AWS::SageMaker::App",
            "AWS::SageMaker::AppImageConfig",
            "AWS::SageMaker::CodeRepository",
            "AWS::SageMaker::DataQualityJobDefinition",
            "AWS::SageMaker::Device",
            "AWS::SageMaker::DeviceFleet",
            "AWS::SageMaker::Domain",
            "AWS::SageMaker::Endpoint",
            "AWS::SageMaker::EndpointConfig",
            "AWS::SageMaker::FeatureGroup",
            "AWS::SageMaker::Image",
            "AWS::SageMaker::Model",
            "AWS::SageMaker::ModelBiasJobDefinition",
            "AWS::SageMaker::ModelExplainabilityJobDefinition",
            "AWS::SageMaker::ModelPackage",
            "AWS::SageMaker::ModelPackageGroup",
            "AWS::SageMaker::ModelQualityJobDefinition",
            "AWS::SageMaker::MonitoringSchedule",
            "AWS::SageMaker::NotebookInstance",
            "AWS::SageMaker::Pipeline",
            "AWS::SageMaker::Project",
            "AWS::SageMaker::UserProfile",
            "AWS::SageMaker::Workteam",
            "AWS::SecretsManager::Secret",
            "AWS::Serverless::Function",
            "AWS::SES::ContactList",
            "AWS::SNS::Topic",
            "AWS::SQS::Queue",
            "AWS::StepFunctions::Activity",
            "AWS::StepFunctions::StateMachine",
            "AWS::SSM::Document",
            "AWS::SSM::MaintenanceWindow",
            "AWS::SSM::Parameter",
            "AWS::SSM::PatchBaseline",
            "AWS::Synthetics::Canary",
            "AWS::WAFv2::IPSet",
            "AWS::WAFv2::RegexPatternSet",
            "AWS::WAFv2::RuleGroup",
            "AWS::WAFv2::WebACL",
            "AWS::WorkSpaces::Workspace",
            "AWS::WorkSpaces::ConnectionAlias",
            "AWS::XRay::SamplingRule",
            "AWS::XRay::Group",
        ]

        yaml = YAML()
        yaml.explicit_start = True
        yaml.preserve_quotes = True
        yaml.line_break = True
        yaml.width = 200


        try:
            with open(filename, encoding='utf-8') as cfn:
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
        """
        Returns a list of the changed tags for a resource
        """
        try:
            return self.stats[resource]["updatedtags"]
        except KeyError:
            return []


    def get_obligatory_tags(self) -> Dict:
        return self.obligatory_tags


    def get_found_tags(self, resource: str) -> List:
        """
        Returns a list of the present tags on a resource
        """
        try:
            return self.stats[resource]["foundtags"]
        except KeyError:
            return []


    def get_added_tags(self, resource: str) -> List:
        """
        Returns a list of the added tags for a resource
        """

        try:
            return self.stats[resource]["addedtags"]
        except KeyError:
            return []

    def get_git_path(self, filename: str) -> str:
        """
        Returns the relative path for a file from the repo root dir
        instead of any abritrary path the user has given us
        """

        if filename.startswith('./'):
            filename = filename.replace('./', '')

        full_path = os.getcwd()
        full_path_with_file = f"{full_path}/{filename}"
        repo = git.Repo('.', search_parent_directories=True)
        repodir = f"{repo.working_tree_dir}/"
        relative_file_path = f"{full_path_with_file}".replace(repodir, '')

        return relative_file_path


    def get_git_tags(self, filename: str) -> dict:
        """
        Returns a dict of gitrepo & gitfile tags
        """

        if self.git:
            try:
                repo = git.Repo(os.getcwd(), search_parent_directories=True)
                remote = repo.remote().url

                # remove any tokens from the remote string
                remote = re.sub('https://[a-zA-Z0-9_]+@', 'https://', remote)
            except git.exc.InValidGitRepositoryError:
                print("FAIL: this is no git repo, please drop the --git argument")
                sys.exit(1)
            else:
                gitdict = { 'gitrepo': remote, 'gitfile': self.get_git_path(filename) }

        return gitdict


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

        for item in self.resources:
            restype = self.resources[item].get("Type")
            if restype in self.resourcetypes_to_tag:
                self.stats[item] = {"foundtags": [], "updatedtags": [], "addedtags": []}
                print(" ")
                print(
                    f"{Fore.CYAN}[{self.filename}][Resource] {item} => {restype}{Style.RESET_ALL}"
                )
                if "Properties" in self.resources[item]:
                    if "Tags" in self.resources[item].get("Properties"):
                        restags = self.resources[item].get("Properties").get("Tags")
                        updated = self.change_tags(taglist=restags, resource=item)
                        self.resources[item]["Properties"]["Tags"] = updated
                else:
                    self.has_properties = False

                for obligtag in self.obligatory_tags.keys():
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
                        if "Properties" in self.resources[item]:
                            if "Tags" not in self.resources[item].get("Properties"):
                                # Resource support tags, but hasn't any
                                self.resources[item]["Properties"]["Tags"] = [addtags]

                            else:
                                self.resources[item].get("Properties").get("Tags").append(
                                    addtags
                                )
                        else:
                            # resource has no Properties defined, this is valid CFN !
                            # So we need to add a Properties block.  Beware that we're in a
                            # obligtag loop, so only add it once
                            if not self.has_properties:
                                self.resources[item].update({'Properties': OrderedDict({'Tags': [addtags]})})
                                self.has_properties = True

                if self.git:
                    found_git_tags = self.get_git_tags(self.filename)
                    gittags = OrderedDict(
                        {
                            "Key": "gitrepo",
                            "Value": found_git_tags['gitrepo']
                        }
                    )
                    if "Tags" in self.resources[item].get("Properties"):
                        self.resources[item].get("Properties").get("Tags").append(
                                gittags
                        )
                    else:
                        self.resources[item]["Properties"]["Tags"] = [gittags]

                    gittags = OrderedDict(
                        {
                            "Key": "gitfile",
                            "Value": found_git_tags['gitfile']
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
            # self.data['AWSTemplateFormatVersion'] = '2010-09-09'
            return yaml.dump(self.data, sys.stdout)
        else:
            print("Writing file...")
            with open(self.filename, "wb") as file:
                return yaml.dump(self.data, file)
