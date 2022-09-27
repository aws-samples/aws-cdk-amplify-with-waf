import os
import uuid

import boto3
from botocore.exceptions import ClientError

# Setup the client
service_client = boto3.client("cloudfront")


def lambda_handler(event, context):

    try:
        service_client.create_invalidation(
            DistributionId=os.environ["DISTRIBUTION_ID"],
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": ["/*"]},
                "CallerReference": str(uuid.uuid4()),
            },
        )

        print("Cache invalidation request submitted successfully")
    except ClientError as e:
        print(e.response["Error"]["Message"])
