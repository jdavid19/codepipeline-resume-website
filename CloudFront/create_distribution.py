import boto3
#from create_response_header_policy import ResponseHeaderPolicy
import sys
import time

sys.path.append('codepipeline-resume-website/')
from CloudFront.create_response_header_policy import ResponseHeaderPolicy

class CloudFrontDistribution():
    def __init__(self, distribution_data) -> None:
        self.cf_client = boto3.client('cloudfront')
        self.header_policy = ResponseHeaderPolicy()
        self.header_policy_id = self.header_policy.create_header_policy()
        self.cname = distribution_data['cname']
        self.root_object = distribution_data['root_object']
        self.domain_id = distribution_data['domain_id']
        self.cache_policy_id = distribution_data['cache_policy_id']
        self.comment = distribution_data['comment']
        self.certificate_arn = distribution_data['certificate_arn']


    def create_distribution(self):
        """
        Important!
        If you add a CNAME for www.example.com to your distribution (Aliases, check distribution_definition), you also must do the following:
        Create (or update) a CNAME record with your DNS service to route queries for www.example.com to d111111abcdef8.cloudfront.net.
        Add a certificate to CloudFront from a trusted certificate authority (CA) that covers the domain name (CNAME) that you add to your distribution, to validate your authorization to use the domain name.
        """

        distribution_definition = {
            'CallerReference': str(time.time()),
            'Aliases': {
                'Quantity': len(self.cname),
                'Items': self.cname
            },
            'DefaultRootObject': self.root_object,
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': self.domain_id, # Use this value to specify the TargetOriginId in a CacheBehavior or DefaultCacheBehavior.
                        'DomainName': self.domain_id, # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html#DownloadDistValuesDomainName
                        'OriginAccessControlId': '', # Update this distribution after creating OriginAccessControl 
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''
                        },
                    },
                ]
            },
            
            'DefaultCacheBehavior': {
                'TargetOriginId': self.domain_id,
                'ViewerProtocolPolicy': 'redirect-to-https',
                'Compress': True,
                'CachePolicyId': self.cache_policy_id, # CachingDisabled https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html
                'ResponseHeadersPolicyId': self.header_policy_id,
            },
            'Comment': self.comment, # Describe distribution
            'PriceClass': 'PriceClass_100',
            'Enabled': True, #  enable or disable the selected distribution.
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': False,
                'ACMCertificateArn': self.certificate_arn, # provide the Amazon Resource Name (ARN) of the ACM certificate. CloudFront only supports ACM certificates in the US East (N. Virginia) Region ( us-east-1).
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021',
            },
            'HttpVersion': 'http2'
        }
        try:
            response = self.cf_client.create_distribution(DistributionConfig=distribution_definition)
            self.response_id = response['Distribution']['Id']
            self.response_arn = response['Distribution']['ARN']
            self.response_domain = response['Distribution']['DomainName']
            print(f"CloudFront Distribution created. ARN - {self.response_arn}")
            return (self.response_id, self.response_arn, self.response_domain)
        
        except self.cf_client.exceptions.DistributionAlreadyExists as e:
            print(e)