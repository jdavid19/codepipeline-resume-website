import boto3
import botocore.exceptions
import sys
sys.path.append('codepipeline-resume-website/')

from Bucket.bucket import S3BucketManager


class CodePipeline:
    def __init__(self, pipeline_name, github_data, bucket_data):
        self.pipeline_name = pipeline_name
        self.github_username = github_data['username']
        self.github_repo = github_data['repository']
        self.github_branch = github_data['branch']
        self.s3_bucket = bucket_data['s3_bucket']
        self.region = bucket_data['region']
        self.artifact_bucket = bucket_data['artifact_bucket']
        self.codepipeline_client = boto3.client('codepipeline')
        self.s3_client = boto3.client('s3')
        
    def create_artifact_bucket(self):
        # Bucket policy for the Artifact Store (S3 Bucket) that AWS CodePipeline uses to store artifacts used by pipelines.
        bucket_policy = {
            "Version": "2012-10-17",
            "Id": "SSEAndSSLPolicy",
            "Statement": [
                {
                    "Sid": "DenyUnEncryptedObjectUploads",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{self.artifact_bucket}/*",
                    "Condition": {
                        "StringNotEquals": {
                            "s3:x-amz-server-side-encryption": "aws:kms"
                        }
                    }
                },
                {
                    "Sid": "DenyInsecureConnections",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": f"arn:aws:s3:::{self.artifact_bucket}/*",
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
        bucket_manager = S3BucketManager(self.artifact_bucket, self.region)
        bucket_manager.create_bucket()
        bucket_manager.set_bucket_policy(bucket_policy)

    def create_pipeline(self):
        pipeline_definition = {
            'name': self.pipeline_name,
            'roleArn': '', # Enter IAM Role ARN
            'artifactStore': {
                'type': 'S3',
                'location': self.artifact_bucket, 
        },
            'stages': [
                {
                    'name': 'Source',
                    'actions': [
                        {
                            'name': 'SourceAction',
                            'actionTypeId': {
                                'category': 'Source',
                                'owner': 'AWS',
                                'provider': 'CodeStarSourceConnection',
                                'version': '1'
                            },
                            'runOrder': 1,
                            'configuration': {
                                'ConnectionArn': '', # Enter IAM Role ARN (CodeStar Connections)
                                'FullRepositoryId': f'{self.github_username}/{self.github_repo}',
                                'BranchName': self.github_branch,
                                'OutputArtifactFormat': 'CODE_ZIP',
                                'DetectChanges': 'true'
                            },
                            'outputArtifacts': [
                                {
                                    'name': 'SourceArtifact'
                                }
                            ],
                            'region': self.region,  # Adjust the region as needed
                            'namespace': "SourceVariables"
                        }
                    ]
                },
                {
                    'name': 'Deploy',
                    'actions': [
                        {
                            'name': 'DeployAction',
                            'actionTypeId': {
                                'category': 'Deploy',
                                'owner': 'AWS',
                                'provider': 'S3',
                                'version': '1'
                            },
                            'runOrder': 1,
                            'configuration': {
                                'BucketName': self.s3_bucket,
                                'Extract': 'true'
                            },
                            'inputArtifacts': [
                                {
                                    'name': 'SourceArtifact'
                                }
                            ],
                            'region': self.region,  # Adjust the region as needed
                            'namespace': 'DeployVariables'
                        }
                    ]
                }
            ],
            'version': 1,
            'executionMode': 'SUPERSEDED',
            'pipelineType': 'V1'
        }

        try:
            self.codepipeline_client.create_pipeline(pipeline=pipeline_definition)
            print("Successfully created the pipeline.")
        except self.codepipeline_client.exceptions.PipelineNameInUseException as e:
            print(f'Pipeline Name already in use. {e}')
        except botocore.exceptions.ClientError as e:
            print(f'Error creating the pipeline. {e}')
        
    def configure_pipeline(self):
        self.create_artifact_bucket()
        self.create_pipeline()
