import os
import boto3

from dotenv import load_dotenv

load_dotenv()
queue = os.getenv("HIGH_PRIORITY_QUEUE")
access_id = os.getenv("ACCESS_ID")
access_key = os.getenv("ACCESS_KEY")

sqs = boto3.client("sqs",
                   region_name="us-east-1",
                   aws_access_key_id=access_id,
                   aws_secret_access_key=access_key
                   )

def get_from_queue():
    response = sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    print(response)
    message = response["Messages"][0]
    receipt_handle = message["ReceiptHandle"]
    print(message)
    sqs.delete_message(
        QueueUrl=queue,
        ReceiptHandle=receipt_handle
    )

def send_to_teams():
    return

get_from_queue()