import boto3

"""
Create Response Header Policy
: After creating the policy, attach the id when creating cloudfront distribution (create_cloudfront.py)
: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/client/create_response_headers_policy.html
"""

class ResponseHeaderPolicy():
    def __init__(self) -> None:
        self.cf_client = boto3.client('cloudfront')

    def create_header_policy(self):
        try:
            response = self.cf_client.create_response_headers_policy(
                ResponseHeadersPolicyConfig={
                    'Comment': 'Custom response header policy for my cloudfront distribution.',
                    'Name': 'MyHeaderPolicy',
                    'CorsConfig': {
                        'AccessControlAllowOrigins': {
                            'Quantity': 1,
                            'Items': [
                                '*',
                            ]
                        },
                        'AccessControlAllowHeaders': {
                            'Quantity': 1,
                            'Items': [
                                '*',
                            ]
                        },
                        'AccessControlAllowMethods': {
                            'Quantity': 1,
                            'Items': [
                                'ALL',
                            ]
                        },
                        'AccessControlAllowCredentials': False,
                        'AccessControlExposeHeaders': {
                            'Quantity': 1,
                            'Items': [
                                'None',
                            ]   
                        },
                        'AccessControlMaxAgeSec': 60,
                        'OriginOverride': True
                    },     
                }
            )
            return response['ResponseHeadersPolicy']['Id']
        except self.cf_client.exceptions.ResponseHeadersPolicyAlreadyExists as e:
            response = self.cf_client.list_response_headers_policies(
                Type= 'custom'
            )
            response_items = response['ResponseHeadersPolicyList']['Items']
            for item in response_items:
                if item['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name'] == 'MyHeaderPolicy':
                    return item['ResponseHeadersPolicy']['Id']