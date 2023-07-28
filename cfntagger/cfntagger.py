from collections import OrderedDict
import os
import re
import sys
import json
from typing import List, Dict
from configparser import ConfigParser
import git
from colorama import Fore, Style
from ruamel.yaml import YAML


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


def load_config():
    """
    This function constructs a JSON string with the tags to add, either found in (in this order):
        - a configfile in the git root dir (or current dir) in ini-file format
        - the envvar CFN_TAGS in json format
    """

    try:
        # Find a .cfntaggerrc in the git root dir
        repo = git.Repo('.', search_parent_directories=True)
        configfile = f"{repo.working_tree_dir}/.cfntaggerrc"
    except git.exc.InvalidGitRepositoryError:
        # This ain't a git repo, just try the current dir
        configfile = "./.cfntaggerrc"

    if not os.path.isfile(configfile):
        #.cfntaggerrc does not exist neither in git root dir or in cwd, use envvars
        print('[INFO] Using config from environment variable')
        return os.getenv('CFN_TAGS')
    else:
        print('[INFO] Using config from config file')

    config = ConfigParser()
    config.optionxform = str
    config.read(configfile)
    config_parser_dict = {s:dict(config.items(s)) for s in config.sections()}
    try:
        configstr = json.dumps(config_parser_dict['Tags'])
    except KeyError:
        print(f"{Fore.RED}[FAIL] Tags section not defined in .cfntaggerrc !{Style.RESET_ALL}")
        sys.exit(1)

    return configstr



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
        self.resourcetypes_json = [
            "AWS::AmplifyUIBuilder::Form",
            "AWS::AmplifyUIBuilder::Component",
            "AWS::AmplifyUIBuilder::Form",
            "AWS::AmplifyUIBuilder::Theme",
            "AWS::ApiGatewayV2::Api",
            "AWS::ApiGatewayV2::DomainName",
            "AWS::ApiGatewayV2::Stage",
            "AWS::ApiGatewayV2::VpcLink",
            "AWS::Batch::ComputeEnvironment",
            "AWS::Batch::JobDefinition",
            "AWS::Batch::JobQueue",
            "AWS::Batch::SchedulingPolicy",
            "AWS::CodeStarNotifications::NotificationRule",
            "AWS::DAX::Cluster",
            "AWS::FIS::ExperimentTemplate",
            "AWS::Glue::Crawler",
            "AWS::Glue::DataQualityRuleset",
            "AWS::Glue::DevEndpoint",
            "AWS::Glue::Job",
            "AWS::Glue::MLTransform",
            "AWS::Glue::Trigger",
            "AWS::Glue::Workflow",
            "AWS::M2::Application",
            "AWS::M2::Environment",
            "AWS::MSK::Cluster",
            "AWS::MSK::ServerlessCluster",
            "AWS::MSK::VpcConnection",
            "AWS::MWAA::Environment",
            "AWS::Pipes::Pipe",
            "AWS::ResilienceHub::App",
            "AWS::ResilienceHub::ResiliencyPolicy",
            "AWS::ResourceExplorer2::Index",
            "AWS::ResourceExplorer2::View",
            "AWS::ServiceCatalogAppRegistry::Application",
            "AWS::ServiceCatalogAppRegistry::AttributeGroup",
            "AWS::SecurityHub::AutomationRule",
            "AWS::SecurityHub::Hub",
            "AWS::SSM::Parameter",
        ]
        self.resourcetypes_to_tag: List = [
            "AWS::ACMPCA::CertificateAuthority",
            "AWS::Amplify::App",
            "AWS::Amplify::Branch",
            "AWS::AmplifyUIBuilder::Component",
            "AWS::AmplifyUIBuilder::Form",
            "AWS::AmplifyUIBuilder::Theme",
            "AWS::AccessAnalyzer::Analyzer",
            "AWS::ApiGatewayV2::Api",
            "AWS::ApiGateway::ClientCertificate",
            "AWS::ApiGateway::DomainName",
            "AWS::ApiGateway::RestApi",
            "AWS::ApiGateway::Stage",
            "AWS::ApiGateway::UsagePlan",
            "AWS::ApiGateway::VpcLink",
            "AWS::ApiGatewayV2::Api",
            "AWS::ApiGatewayV2::DomainName",
            "AWS::ApiGatewayV2::Stage",
            "AWS::ApiGatewayV2::VpcLink",
            "AWS::AppConfig::Application",
            "AWS::AppConfig::ConfigurationProfile",
            "AWS::AppConfig::Deployment",
            "AWS::AppConfig::DeploymentStrategy",
            "AWS::AppConfig::Environment",
            "AWS::AppConfig::Extension",
            "AWS::AppConfig::ExtensionAssociation",
            "AWS::AppFlow::Flow",
            "AWS::AppIntegrations::DataIntegration",
            "AWS::AppIntegrations::EventIntegration",
            "AWS::ApplicationInsights::Application",
            "AWS::AppMesh::GatewayRoute",
            "AWS::AppMesh::Mesh",
            "AWS::AppMesh::Route",
            "AWS::AppMesh::VirtualGateway",
            "AWS::AppMesh::VirtualNode",
            "AWS::AppMesh::VirtualRouter",
            "AWS::AppMesh::VirtualService",
            "AWS::AppStream::AppBlock",
            "AWS::AppStream::AppBlockBuilder",
            "AWS::AppStream::Application",
            "AWS::AppStream::Fleet",
            "AWS::AppStream::ImageBuilder",
            "AWS::AppStream::Stack",
            "AWS::AppSync::GraphQLApi",
            "AWS::APS::RuleGroupsNamespace",
            "AWS::APS::Workspace",
            "AWS::Athena::CapacityReservation",
            "AWS::Athena::DataCatalog",
            "AWS::Athena::WorkGroup",
            "AWS::AuditManager::Assessment",
            "AWS::BackupGateway::Hypervisor",
            "AWS::Batch::ComputeEnvironment",
            "AWS::Batch::JobDefinition",
            "AWS::Batch::JobQueue",
            "AWS::Batch::SchedulingPolicy",
            "AWS::BillingConductor::BillingGroup",
            "AWS::BillingConductor::CustomLineItem",
            "AWS::BillingConductor::PricingPlan",
            "AWS::BillingConductor::PricingRule",
            "AWS::Cassandra::Keyspace",
            "AWS::Cassandra::Table",
            "AWS::CertificateManager::Certificate",
            "AWS::CleanRooms::Collaboration",
            "AWS::CleanRooms::ConfiguredTable",
            "AWS::CleanRooms::ConfiguredTableAssociation",
            "AWS::CleanRooms::Membership",
            "AWS::Cloud9::EnvironmentEC2",
            "AWS::CloudFormation::Stack",
            "AWS::CloudFormation::StackSet",
            "AWS::CloudFront::Distribution",
            "AWS::CloudFront::StreamingDistribution",
            "AWS::CloudTrail::Channel",
            "AWS::CloudTrail::EventDataStore",
            "AWS::CloudTrail::Trail",
            "AWS::CloudWatch::InsightRule",
            "AWS::CloudWatch::MetricStream",
            "AWS::CodeBuild::Project",
            "AWS::CodeBuild::ReportGroup",
            "AWS::CodeArtifact::Domain",
            "AWS::CodeArtifact::Repository",
            "AWS::CodeCommit::Repository",
            "AWS::CodeDeploy::Application",
            "AWS::CodeDeploy::DeploymentGroup",
            "AWS::CodeGuruProfiler::ProfilingGroup",
            "AWS::CodeGuruReviewer::RepositoryAssociation",
            "AWS::CodePipeline::CustomActionType",
            "AWS::CodePipeline::Pipeline",
            "AWS::CodeStarConnections::Connection",
            "AWS::CodeStarNotifications::NotificationRule",
            "AWS::Comprehend::DocumentClassifier",
            "AWS::Comprehend::Flywheel",
            "AWS::Config::AggregationAuthorization",
            "AWS::Config::ConfigurationAggregator",
            "AWS::Config::StoredQuery",
            "AWS::Connect::ContactFlow",
            "AWS::Connect::ContactFlowModule",
            "AWS::Connect::EvaluationForm",
            "AWS::Connect::HoursOfOperation",
            "AWS::Connect::PhoneNumber",
            "AWS::Connect::Prompt",
            "AWS::Connect::QuickConnect",
            "AWS::Connect::Rule",
            "AWS::Connect::TaskTemplate",
            "AWS::Connect::User",
            "AWS::ConnectCampaigns::Campaign",
            "AWS::CustomerProfiles::CalculatedAttributeDefinition",
            "AWS::CustomerProfiles::Domain",
            "AWS::CustomerProfiles::EventStream",
            "AWS::CustomerProfiles::Integration",
            "AWS::CustomerProfiles::ObjectType",
            "AWS::DataBrew::Dataset",
            "AWS::DataBrew::Job",
            "AWS::DataBrew::Project",
            "AWS::DataBrew::Recipe",
            "AWS::DataBrew::Ruleset",
            "AWS::DataBrew::Schedule",
            "AWS::DLM::LifecyclePolicy",
            "AWS::DataSync::Agent",
            "AWS::DataSync::LocationEFS",
            "AWS::DataSync::LocationFSxLustre",
            "AWS::DataSync::LocationFSxONTAP",
            "AWS::DataSync::LocationFSxOpenZFS",
            "AWS::DataSync::LocationFSxWindows",
            "AWS::DataSync::LocationHDFS",
            "AWS::DataSync::LocationNFS",
            "AWS::DataSync::LocationObjectStorage",
            "AWS::DataSync::LocationS3",
            "AWS::DataSync::LocationSMB",
            "AWS::DataSync::StorageSystem",
            "AWS::DataSync::Task",
            "AWS::DAX::Cluster",
            "AWS::Detective::Graph",
            "AWS::DeviceFarm::DevicePool",
            "AWS::DeviceFarm::InstanceProfile",
            "AWS::DeviceFarm::NetworkProfile",
            "AWS::DeviceFarm::Project",
            "AWS::DeviceFarm::TestGridProject",
            "AWS::DeviceFarm::VPCEConfiguration",
            "AWS::DMS::Endpoint",
            "AWS::DMS::EventSubscription",
            "AWS::DMS::ReplicationInstance",
            "AWS::DMS::ReplicationSubnetGroup",
            "AWS::DMS::ReplicationTask",
            "AWS::DocDB::DBCluster",
            "AWS::DocDB::DBClusterParameterGroup",
            "AWS::DocDB::DBInstance",
            "AWS::DocDB::DBSubnetGroup",
            "AWS::DocDBElastic::Cluster",
            "AWS::DynamoDB::Table",
            "AWS::EC2::CarrierGateway",
            "AWS::EC2::CustomerGateway",
            "AWS::EC2::DHCPOptions",
            "AWS::EC2::EIP",
            "AWS::EC2::FlowLog",
            "AWS::EC2::Instance",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::IPAM",
            "AWS::EC2::IPAMPool",
            "AWS::EC2::IPAMResourceDiscovery",
            "AWS::EC2::IPAMResourceDiscoveryAssociation",
            "AWS::EC2::KeyPair",
            "AWS::EC2::LocalGatewayRouteTable",
            "AWS::EC2::LocalGatewayRouteTableVirtualInterfaceGroupAssociation",
            "AWS::EC2::LocalGatewayRouteTableVPCAssociation",
            "AWS::EC2::NatGateway",
            "AWS::EC2::NetworkAcl",
            "AWS::EC2::NetworkInsightsAccessScope",
            "AWS::EC2::NetworkInsightsAccessScopeAnalysis",
            "AWS::EC2::NetworkInsightsAnalysis",
            "AWS::EC2::NetworkInsightsPath",
            "AWS::EC2::NetworkInterface",
            "AWS::EC2::PlacementGroup",
            "AWS::EC2::PrefixList",
            "AWS::EC2::RouteTable",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::Subnet",
            "AWS::EC2::TrafficMirrorFilter",
            "AWS::EC2::TrafficMirrorSession",
            "AWS::EC2::TrafficMirrorTarget",
            "AWS::EC2::TransitGateway",
            "AWS::EC2::TransitGatewayAttachment",
            "AWS::EC2::TransitGatewayConnect",
            "AWS::EC2::TransitGatewayMulticastDomain",
            "AWS::EC2::TransitGatewayPeeringAttachment",
            "AWS::EC2::TransitGatewayRouteTable",
            "AWS::EC2::TransitGatewayVpcAttachment",
            "AWS::EC2::VerifiedAccessEndpoint",
            "AWS::EC2::VerifiedAccessGroup",
            "AWS::EC2::VerifiedAccessInstance",
            "AWS::EC2::VerifiedAccessTrustProvider",
            "AWS::EC2::VPNConnection",
            "AWS::EC2::VPNGateway",
            "AWS::EC2::Volume",
            "AWS::EC2::VPC",
            "AWS::ECR::PublicRepository",
            "AWS::ECR::Repository",
            "AWS::ECS::CapacityProvider",
            "AWS::ECS::Cluster",
            "AWS::ECS::ContainerInstance",
            "AWS::ECS::Service",
            "AWS::ECS::Task",
            "AWS::ECS::TaskDefinition",
            "AWS::EKS::Cluster",
            "AWS::EKS::Addon",
            "AWS::EKS::NodeGroup",
            "AWS::EKS::FargateProfile",
            "AWS::EKS::IdentityProviderConfig",
            "AWS::ElasticBeanstalk::Environment",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ParameterGroup",
            "AWS::ElastiCache::SecurityGroup",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::ElastiCache::SubnetGroup",
            "AWS::ElastiCache::Snapshot",
            "AWS::ElasticLoadBalancing::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            "AWS::ElasticSearch::Domain",
            "AWS::EMR::Cluster",
            "AWS::EMR::Studio",
            "AWS::EMRServerless::Application",
            "AWS::EMRContainers::VirtualCluster",
            "AWS::Events::EventBus",
            "AWS::Evidently::Experiment",
            "AWS::Evidently::Feature",
            "AWS::Evidently::Launch",
            "AWS::Evidently::Project",
            "AWS::Evidently::Segment",
            "AWS::FinSpace::Environment",
            "AWS::FIS::ExperimentTemplate",
            "AWS::FMS::Policy",
            "AWS::FMS::ResourceSet",
            "AWS::Forecast::Dataset",
            "AWS::Forecast::DatasetGroup",
            "AWS::FraudDetector::Detector",
            "AWS::FraudDetector::EntityType",
            "AWS::FraudDetector::EventType",
            "AWS::FraudDetector::Label",
            "AWS::FraudDetector::List",
            "AWS::FraudDetector::Outcome",
            "AWS::FraudDetector::Variable",
            "AWS::FSx::DataRepositoryAssociation",
            "AWS::FSx::FileSystem",
            "AWS::FSx::Snapshot",
            "AWS::FSx::StorageVirtualMachine",
            "AWS::FSx::Volume",
            "AWS::GlobalAccelerator::Accelerator",
            "AWS::Glue::Crawler",
            "AWS::Glue::DataQualityRuleset",
            "AWS::Glue::DevEndpoint",
            "AWS::Glue::MLTransform",
            "AWS::Glue::Job",
            "AWS::Glue::Registry",
            "AWS::Glue::Schema",
            "AWS::Glue::Trigger",
            "AWS::Glue::Workflow",
            "AWS::GroundStation::Config",
            "AWS::GroundStation::DataflowEndpointGroup",
            "AWS::GroundStation::MissionProfile",
            "AWS::GuardDuty::Detector",
            "AWS::GuardDuty::Filter",
            "AWS::GuardDuty::IPSet",
            "AWS::GuardDuty::ThreatIntelSet",
            "AWS::HealthLake::FHIRDatastore",
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
            "AWS::InternetMonitor::Monitor",
            "AWS::Kendra::DataSource",
            "AWS::Kendra::Faq",
            "AWS::Kendra::Index",
            "AWS::KendraRanking::ExecutionPlan",
            "AWS::SSMIncidents::ReplicationSet",
            "AWS::SSMIncidents::ResponsePlan",
            "AWS::KMS::Key",
            "AWS::KMS::ReplicaKey",
            "AWS::Kinesis::Stream",
            "AWS::KinesisAnalyticsV2::Application",
            "AWS::KinesisFirehose::DeliveryStream",
            "AWS::KinesisVideo::SignalingChannel",
            "AWS::KinesisVideo::Stream",
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
            "AWS::LookoutEquipment::InferenceScheduler",
            "AWS::M2::Application",
            "AWS::M2::Environment",
            "AWS::Macie::AllowList",
            "AWS::ManagedBlockchain::Accessor",
            "AWS::AmazonMQ::Broker",
            "AWS::AmazonMQ::Configuration",
            "AWS::MemoryDB::User",
            "AWS::MemoryDB::ACL",
            "AWS::MemoryDB::Cluster",
            "AWS::MemoryDB::ParameterGroup",
            "AWS::MemoryDB::SubnetGroup",
            "AWS::MSK::Cluster",
            "AWS::MSK::ServerlessCluster",
            "AWS::MSK::VpcConnection",
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
            "AWS::OpenSearchServerless::Collection",
            "AWS::OpsWorks::Layer",
            "AWS::OpsWorks::Stack",
            "AWS::OpsWorksCM::Server",
            "AWS::Organizations::Account",
            "AWS::Organizations::OrganizationalUnit",
            "AWS::Organizations::Policy",
            "AWS::Organizations::ResourcePolicy",
            "AWS::OSIS::Pipeline",
            "AWS::Panorama::ApplicationInstance",
            "AWS::Panorama::Package",
            "AWS::Pipes::Pipe",
            "AWS::Proton::EnvironmentAccountConnection",
            "AWS::Proton::EnvironmentTemplate",
            "AWS::Proton::ServiceTemplate",
            "AWS::QLDB::Ledger",
            "AWS::QLDB::Stream",
            "AWS::QuickSight::Theme",
            "AWS::QuickSight::Analysis",
            "AWS::QuickSight::Dashboard",
            "AWS::QuickSight::DataSet",
            "AWS::QuickSight::DataSource",
            "AWS::QuickSight::Template",
            "AWS::RAM::Permission",
            "AWS::RAM::ResourceShare",
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
            "AWS::RedshiftServerless::Namespace",
            "AWS::RedshiftServerless::Workgroup",
            "AWS::Rekognition::Collection",
            "AWS::Rekognition::StreamProcessor",
            "AWS::ResilienceHub::App",
            "AWS::ResilienceHub::ResiliencyPolicy",
            "AWS::ResourceExplorer2::Index",
            "AWS::ResourceExplorer2::View",
            "AWS::Route53RecoveryControl::Cluster",
            "AWS::Route53RecoveryControl::ControlPanel",
            "AWS::Route53RecoveryControl::SafetyRule",
            "AWS::Route53Resolver::FirewallDomainList",
            "AWS::Route53Resolver::FirewallRuleGroup",
            "AWS::Route53Resolver::FirewallRuleGroupAssociation",
            "AWS::Route53Resolver::ResolverEndpoint",
            "AWS::Route53Resolver::ResolverRule",
            "AWS::RUM::AppMonitor",
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
            "AWS::Scheduler::ScheduleGroup",
            "AWS::SecretsManager::Secret",
            "AWS::Serverless::Function",
            "AWS::ServiceCatalog::CloudFormationProduct",
            "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
            "AWS::ServiceCatalog::Portfolio",
            "AWS::ServiceCatalogAppRegistry::Application",
            "AWS::ServiceCatalogAppRegistry::AttributeGroup",
            "AWS::SecurityHub::AutomationRule",
            "AWS::SecurityHub::Hub",
            "AWS::SES::ContactList",
            "AWS::Shield::Protection",
            "AWS::Shield::ProtectionGroup",
            "AWS::SNS::Topic",
            "AWS::SQS::Queue",
            "AWS::StepFunctions::Activity",
            "AWS::StepFunctions::StateMachine",
            "AWS::SSM::Document",
            "AWS::SSM::MaintenanceWindow",
            "AWS::SSM::Parameter",
            "AWS::SSM::PatchBaseline",
            "AWS::Synthetics::Canary",
            "AWS::Synthetics::Group",
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

        obligatory_tags_str = load_config()
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


    def cfntransformer(self, s: str) -> str:
        """
        This function removes faulty tag formatting from a yaml.dump result
        """

        cfnlist = s.split('\n')
        UseJsonTags = False
        TagBlock = False

        for i, line in enumerate(cfnlist):
            # Python 3 interprets string literals as Unicode strings
            # and therefore \s is treated as an escaped Unicode character.
            # We must declare our RegEx pattern as a raw string by prepending r

            if re.search(r'^\s+Type:\s*AWS', line):
                # Extracting the resource type from Type: AWS::xx::yy
                ResourceType = ':'.join(line.split(':')[1:]).strip()
                UseJsonTags =  ResourceType in self.resourcetypes_json

            if line.strip().startswith('Tags:'):
                TagBlock = True
                if cfnlist[i-1] == '':
                    # we have an empty line before a tag block, let's remove it
                    del cfnlist[i-1]

            if re.search(r'^\s+\w:\s*$', line):
                # Single word followed by a colon --> start of a new resource block
                TagBlock = False

            if TagBlock and UseJsonTags and line.strip().startswith('- Key:'):
                tagvalue = ''.join(cfnlist[i+1].strip().split(':')[1:]).strip()
                cfnlist[i] = line.replace('- Key:', " ")
                cfnlist[i] += f": {tagvalue}"
                del cfnlist[i+1]

        return '\n'.join(cfnlist)


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
            return yaml.dump(self.data, sys.stdout, transform=self.cfntransformer)
        else:
            print("Writing file...")
            with open(self.filename, "w", encoding='utf-8') as file:
                return yaml.dump(self.data, file, transform=self.cfntransformer)
