# Python Project with Boto3

This project is a Python application that utilizes the Boto3 library to interact with various AWS services programmatically. This Python application is based on my previous project [Deploying a Static Website with Amazon S3, AWS CodePipeline, Amazon Route 53, and Amazon CloudFront.](https://github.com/jdavid19/resume-website-v2/tree/main)

## Prerequisites

Before you begin, make sure you have the following:

- Python installed on your local machine.
- AWS account credentials configured either through environment variables or the AWS CLI.
- Boto3 library installed (`pip install boto3`).

## Getting Started

1. Clone this repository to your local machine:

    ```
    git clone <repository-url>
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Set up AWS credentials either through environment variables:

    ```bash
    export AWS_ACCESS_KEY_ID=<your-access-key-id>
    export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
    ```
    or AWS CLI:
   ```
   aws configure
   ```

5. Run the Python script/s (main.py) to interact with AWS services.



## Additional Resources

- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS SDK for Python (Boto3) GitHub Repository](https://github.com/boto/boto3)
- [AWS SDK for Python (Boto3) AWS Documentation](https://docs.aws.amazon.com/pythonsdk/?icmpid=docs_homepage_sdktoolkits)
