import boto3
import sys
sys.path.append('codepipeline-resume-website/')
from CloudFront.origin_access_control import OriginAccessControl

"""
Update CloudFront Distribution to attach Origin Access Control Id
: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/client/update_distribution.html
: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_UpdateDistribution.html
"""

class DistributionConfig():
    def __init__(self) -> None:
        self.cf_client = boto3.client('cloudfront')
        self.origin_access = OriginAccessControl()
        self.origin_access_id = self.origin_access.create_originacess()

    def get_distribution_config(self, distribution_id):
        try:
            response = self.cf_client.get_distribution_config(
                Id= distribution_id
            )
            self.response = {key: value for key, value in response.items() if key != 'ResponseMetadata'}
        except self.cf_client.exceptions.NoSuchDistribution as e:
            print(e)

    def update_distribution_config(self, distribution_id):
        self.response['IfMatch'] = self.response.pop('ETag')
        for item in self.response['DistributionConfig']['Origins']['Items']:
            if item['OriginAccessControlId'] == '':
                item['OriginAccessControlId'] = f"{self.origin_access_id}"
        self.response['Id'] = f"{distribution_id}"
        
    def update_distribution(self):
        try:
            response = self.cf_client.update_distribution(
                DistributionConfig= self.response['DistributionConfig'],
                Id = self.response['Id'],
                IfMatch = self.response['IfMatch']
            )
            print("CloudFront distribution successfully updated.")
            return response
        except self.cf_client.exceptions.IllegalUpdate as e:
            print(e)

