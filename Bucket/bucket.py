import boto3
import json

class S3BucketManager:
    def __init__(self, bucket_name, region):
        self.s3_client = boto3.client('s3', region_name=region)
        self.bucket_name = bucket_name
        self.region = region

    def create_bucket(self):
        try:
            self.s3_client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            print(f'Bucket {self.bucket_name} created successfully.')
        except self.s3_client.exceptions.BucketAlreadyExists as e:
            print(f'Bucket name already exists. Please choose a different name. {e}')
            pass
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou as e:
            print(f'Bucket is already owned by you. {e}')
            pass

    def block_public_access(self, public_access_block_config):
        try:
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration=public_access_block_config
            )
            print(f'Public access enabled for bucket {self.bucket_name}.')
        except Exception as e:
            print(f'Error enabling public access: {e}')

    def enable_static_website_hosting(self):
        website_configuration = {
            'IndexDocument': {'Suffix': 'index.html'}
        }
        try:
            self.s3_client.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration=website_configuration
            )
            print(f'Static website hosting enabled for bucket {self.bucket_name}.')
        except Exception as e:
            print(f'Error enabling static website hosting: {e}')

    def set_bucket_policy(self, policy):
        try:
            policy_json = json.dumps(policy)
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=policy_json
            )
            print(f'Bucket policy added to {self.bucket_name} successfully.')
        except Exception as e:
            print(f'Error adding bucket policy: {e}')

    def configure_bucket(self):
        self.create_bucket()
        public_access_block_config = {
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
        self.block_public_access(public_access_block_config)
        self.enable_static_website_hosting()
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]
        }
        self.set_bucket_policy(bucket_policy)