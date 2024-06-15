import boto3
import botocore.exceptions as bexcept
import time

class AWSCertificateManager:
    def __init__(self, region_name='us-east-1'):
        self.acm_client = boto3.client('acm', region_name=region_name)

    def request_certificate(self, domain_name, alt_name, validation_method='DNS'):
        try:
            response = self.acm_client.request_certificate(
                DomainName=domain_name,
                ValidationMethod=validation_method,
                SubjectAlternativeNames=[
                    alt_name,
                ]
            )
            return response['CertificateArn']
        except self.acm_client.exceptions.InvalidDomainValidationOptionsException as e:
            print(f"Invalid Domain Validation Option. {e}")
        except self.acm_client.exceptions.InvalidParameterException as e:
            print(f"Invalid parameter. {e}")
        except bexcept.ClientError as e:
            print(f"Error requesting certificate. {e}")

    def get_certificate_cname(self, certificate_arn):
        try:
            while True:
                response = self.acm_client.describe_certificate(CertificateArn=certificate_arn)
                options = response['Certificate']['DomainValidationOptions']
                if 'ResourceRecord' in options[0]:
                    return options[0]['ResourceRecord']
                print('Waiting for certificate validation options...')
                time.sleep(10)
        except self.acm_client.exceptions.ResourceNotFoundException as e:
            print(f"Resource not found. {e}")
        except bexcept.ClientError as e:
            print(f"Error fetching the certificate data. {e}")