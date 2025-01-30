import json
import os

import boto3
import pymsteams

from dotenv import load_dotenv

load_dotenv()
# Environment variables
queue = os.getenv("HIGH_PRIORITY_QUEUE")
access_id = os.getenv("AWS_ACCESS_KEY_ID")
access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
teams = os.getenv("TEAMS_WEBHOOK")

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
        WaitTimeSeconds=20
    )

    if "Messages" not in response:
        return None

    message = response["Messages"][0]

    return message


def send_to_teams(message_to_send):
    print("Sending...")
    outgoing = pymsteams.connectorcard(teams)
    message_json = json.loads(message_to_send["Body"])
    priority = message_json['priority'].capitalize()
    body: str = message_json['message']
    body = body.replace("\n", "<br>")
    outgoing.text(f"<h1 style='font-weight: bold'>{priority} priority: {message_json['title']}</h1>"
                  f"<p>{body}</p>")
    outgoing.send()

def run():
    while True:
        message = get_from_queue()
        if message:
            try:
                send_to_teams(message)
            except pymsteams.TeamsWebhookException as ex:
                print(ex)
                continue

            receipt_handle = message["ReceiptHandle"]

            sqs.delete_message(
                QueueUrl=queue,
                ReceiptHandle=receipt_handle
            )

if __name__ == "__main__":
    run()
