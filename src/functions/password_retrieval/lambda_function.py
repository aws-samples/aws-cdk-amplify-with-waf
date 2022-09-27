import base64
import os

import boto3

# Setup the client
service_client = boto3.client("secretsmanager")


def lambda_handler(event, context):
    current_username = service_client.get_secret_value(
        SecretId=os.environ["USERNAME_SECRET_ARN"], VersionStage="AWSCURRENT"
    )

    current_password = service_client.get_secret_value(
        SecretId=os.environ["CREDENTIALS_SECRET_ARN"], VersionStage="AWSCURRENT"
    )

    credentials_suffix = (
        f"{current_username['SecretString']}:{current_password['SecretString']}"
    )

    # Encode suffix in base64
    bytes_encoded_suffix = base64.b64encode(bytes(credentials_suffix, "utf-8"))
    encoded_suffix = bytes_encoded_suffix.decode("utf-8")

    return {
        "Data": {
            "EncodedSuffix": f"Basic {encoded_suffix}",  # For CloudFront Authorization header
            "EncodedCredentials": encoded_suffix,  # For Amplify Basic Auth credentials
        },
    }
