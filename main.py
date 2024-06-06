import sys
import random

sys.path.append('codepipeline-resume-website/')

from Bucket.bucket import S3BucketManager
from CodePipeline.pipeline import CodePipeline
from Route53.hostedzone import Route53Manager
from CertificateManager.certificate import AWSCertificateManager
from CloudFront.create_distribution import CloudFrontDistribution
from CloudFront.update_distribution import DistributionConfig


class S3StaticWebsite():
    def __init__(self, bucket_name, region):
        self.bucket_name = bucket_name
        self.region = region

    def s3_bucket(self):
        manager = S3BucketManager(self.bucket_name, self.region)
        manager.configure_bucket()

class PipelineS3Github():
    def __init__(self, pipeline_name, random_integer, bucket_data, github_data):
        self.pipeline_name = pipeline_name
        self.random_integer = random_integer
        self.bucket_data = bucket_data
        self.github_data = github_data
    
    def manage_pipeline(self):
        manager = CodePipeline(self.pipeline_name, self.github_data, self.bucket_data)
        manager.configure_pipeline()

class Route53HostedZone():
    def __init__(self, hostedzone_data):
        self.domain_name = hostedzone_data['domain_name']
        self.record_action = hostedzone_data['record_action']
        self.alias_target_dns = hostedzone_data['alias_target_dns']
        self.alias_hosted_zone_id = hostedzone_data['alias_hosted_zone_id']
        self.route53_manager = Route53Manager()

    def create_hostedzone(self):
        hosted_zone_id = self.route53_manager.create_hosted_zone(self.domain_name)
        return hosted_zone_id
    
    def create_A_record(self, hosted_zone_id):
        alias_a_record_response = self.route53_manager.create_alias_a_record(
            hosted_zone_id, self.record_action, self.domain_name, self.alias_target_dns, self.alias_hosted_zone_id
        )
        print("Alias A record created:", alias_a_record_response)

    def create_cname_record(self, hosted_zone_id, cname_record):
        cname_response = self.route53_manager.create_cname_record(hosted_zone_id, cname_record)
        return cname_response 

class CertificateManager():
    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.certificate_manager = AWSCertificateManager()

    def request_public_certificate(self):
        certificate_arn = self.certificate_manager.request_certificate(self.domain_name)
        return certificate_arn
    
    def get_cname_record(self, certificate_arn):
        cname_record = self.certificate_manager.get_certificate_cname(certificate_arn)
        return cname_record
    
class CloudFront():
    def __init__(self, distribution_data):
        self.cloudfront_manager = CloudFrontDistribution(distribution_data)

    def create_distribution(self):
        distribution_response = self.cloudfront_manager.create_distribution()
        return distribution_response
        
    # Giving the origin access control permission to access the S3 bucket
    # S3 bucket policy that allows read-only access to a CloudFront OAC
    def update_bucket_config(self, bucket_name, region, distribution_arn):
        bucket_policy = {
            "Version": "2008-10-17",
            "Id": "PolicyForCloudFrontPrivateContent",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/*",
                        f"arn:aws:s3:::{bucket_name}/images/*"
                    ],
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": f"{distribution_arn}"
                        }
                    }
                }
            ]
        }

        public_access_block_config = {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }

        bucket_manager = S3BucketManager(bucket_name, region)
        bucket_manager.set_bucket_policy(bucket_policy)
        bucket_manager.block_public_access(public_access_block_config)

    # Update CloudFront Distribution to attach Origin Access Control Id
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/client/update_distribution.html
    def add_oac_distribution(self, distribution_id):
        origin_access_manager = DistributionConfig()
        origin_access_manager.get_distribution_config(distribution_id)
        origin_access_manager.update_distribution_config(distribution_id)
        origin_access_manager.update_distribution()


def main():
    """
    Step 1: Create S3 Bucket as a Origin for the files of your static website.
        Note: If you will setup a Domain Name for your static website, make sure the domain name matches the bucket name. 
    """
    bucket_name = 'jd-espiritu.website'
    region = 'ap-southeast-1'
    bucket_manager = S3StaticWebsite(bucket_name, region)
    bucket_manager.s3_bucket()

    """
    Step 2: Create a pipeline in AWSCodePipeline
    """
    pipeline_name = 'jd-espiritu-pipeline'
    random_integer = random.randint(10**11, (10**12)-1)
    bucket_data = {
        's3_bucket' : bucket_name,
        'artifact_bucket' : f'pipeline-artifact-bucket-ap-southeast-1-{random_integer}',
        'region' : region
    }
    github_data = {
        'username' : 'jdavid19',
        'repository' : 'resume-website-v2',
        'branch' : 'main'
    }
    pipeline_manager = PipelineS3Github(pipeline_name, random_integer, bucket_data, github_data)
    pipeline_manager.manage_pipeline()
    
    """
    Step 3: Create Hosted Zone in Route 53 (in my case, I purchased the domain from a 3rd party registrar)
        Note: If you purchased the domain name in Route53, it will automatically create the hosted zone. You can skip this step.
        After this step, you can check and verify if your static website is up and running using your purchased domain name.
    """
    hostedzone_data = {
        'domain_name' : f'{bucket_name}',
        'record_action' : 'CREATE',
        'alias_target_dns' : 's3-website-ap-southeast-1.amazonaws.com',
        'alias_hosted_zone_id' : 'Z3O0J2DXBE1FTB',
    }
    hostedzone_manager = Route53HostedZone(hostedzone_data)
    hostedzone_id = hostedzone_manager.create_hostedzone()
    print(f"Hosted Zone created with ID: {hostedzone_id}")
    hostedzone_manager.create_A_record(hostedzone_id)

    """
    Step 4: Request public certificate from AWS Certificate Manager
    """
    certificate_manager = CertificateManager(hostedzone_data['domain_name'])
    certificate_arn = certificate_manager.request_public_certificate()
    print(f"Certificate requested with ARN: {certificate_arn}")

    """
    Step 5 : Validate Domain Ownership
    """
    # Get CNAME record for certificate validation
    cname_record = certificate_manager.get_cname_record(certificate_arn)
    print(f"CNAME record for validation: {cname_record}")

    # Create CNAME record in Route 53
    cname_response = hostedzone_manager.create_cname_record(hostedzone_id, cname_record)
    print("CNAME record created:", cname_response)

    """
    Step 6: Create CloudFront Distribution
        Giving the origin access control permission to access the S3 bucket
    """
    distribution_data = {
        'cname' : f"{hostedzone_data['domain_name']}",
        'root_object' : 'index.html',
        'domain_id' : f'{bucket_name}.s3.{region}.amazonaws.com',
        'cache_policy_id' : '4135ea2d-6df8-44a3-9df3-4b5a84be39ad', # CachingDisabled https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html
        'comment' : f'Test Distribution for {bucket_name}',
        'certificate_arn' : certificate_arn
    }

    cloudfront_manager = CloudFront(distribution_data)
    distribution_response = cloudfront_manager.create_distribution()
    distribution_id = distribution_response[0]
    distribution_arn = distribution_response[1]
    distribution_domain = distribution_response[2]
    cloudfront_manager.update_bucket_config(bucket_name, region, distribution_arn)
    cloudfront_manager.add_oac_distribution(distribution_id)

    """
    Step 7: Update the A record in Hosted Zone
    """
    hostedzone_data.update({
        'record_action' : 'UPSERT',
        'alias_target_dns' : distribution_domain,
        'alias_hosted_zone_id' : 'Z2FDTNDATAQYW2' #This is always the hosted zone ID when you create an alias record that routes traffic to a CloudFront distribution. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset-aliastarget.html
    })
    hostedzone_manager = Route53HostedZone(hostedzone_data)
    hostedzone_manager.create_A_record(hostedzone_id)


if __name__ == "__main__":
    main()