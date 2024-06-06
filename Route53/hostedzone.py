import boto3
import time
import botocore.exceptions as bexcept

class Route53Manager:
    def __init__(self):
        self.route53_client = boto3.client('route53')

    def create_hosted_zone(self, domain_name):
        try:
            response = self.route53_client.create_hosted_zone(
                Name=domain_name,
                CallerReference=str(time.time()),
                HostedZoneConfig={
                        'Comment': f'Hosted zone for {domain_name}',
                        'PrivateZone': False
                    }
            )
            return response['HostedZone']['Id']
        except self.route53_client.exceptions.HostedZoneAlreadyExists as e:
                print(f"Hosted zone for domain {domain_name} already exists.")
        except bexcept.ClientError as e:
            print(f"Error creating hosted zone: {e}")
    
    def create_alias_a_record(self, hosted_zone_id, record_action, domain_name, alias_target_dns, alias_hosted_zone_id):
        try:
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': record_action,
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'AliasTarget': {
                                    'HostedZoneId': alias_hosted_zone_id,
                                    'DNSName': alias_target_dns,
                                    'EvaluateTargetHealth': False
                                }
                            }
                        }
                    ]
                }
            )
            return response
        except bexcept.ClientError as e:
            print(f"Error creating alias A record: {e}")

    def create_cname_record(self, hosted_zone_id, cname_record):
        try:
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'CREATE',
                            'ResourceRecordSet': {
                                'Name': cname_record['Name'],
                                'Type': cname_record['Type'],
                                'TTL': 300,
                                'ResourceRecords': [{'Value': cname_record['Value']}]
                            }
                        }
                    ]
                }
            )
            return response
        except bexcept.ClientError as e:
            print(f"Error creating CNAME record: {e}")