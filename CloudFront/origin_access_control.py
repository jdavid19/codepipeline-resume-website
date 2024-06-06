import boto3

"""
PREREQUISITES:
Before you create and set up origin access control (OAC), you must have a CloudFront distribution (create_cloudfront.py) with an Amazon S3 bucket origin.
This origin must be a regular S3 bucket, not a bucket configured as a website endpoint.
When you use OAC to secure your S3 bucket origin, communication between CloudFront and Amazon S3 is always through HTTPS, regardless of your specific settings.
"""


class OriginAccessControl():
    def __init__(self) -> None:
        self.cf_client = boto3.client('cloudfront')
        self.oac_name = "jd-espiritu.website"

    def create_originacess(self):
        try:
            response = self.cf_client.create_origin_access_control(
                OriginAccessControlConfig={
                    'Name': self.oac_name,
                    'Description': f'Restrict public access to the origin: {self.oac_name} ',
                    'SigningProtocol': 'sigv4',
                    'SigningBehavior': 'always',
                    'OriginAccessControlOriginType': 's3'
                }
            )
            print(f"Created Origin Access Control : {response['OriginAccessControl']['Id']}")
            return response['OriginAccessControl']['Id']
            
        except self.cf_client.exceptions.OriginAccessControlAlreadyExists as e:
            if True:
                # print(f"Origin Access Control Already Exists.")
                response = self.cf_client.list_origin_access_controls()
                for item in response['OriginAccessControlList']['Items']:
                    if item['Name'] == self.oac_name:
                        return item['Id']
                    
                