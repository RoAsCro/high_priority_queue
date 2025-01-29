import json
import os
from threading import Thread

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
run = False

def get_from_queue():

    response = sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )

    if "Messages" not in response:
        return

    message = response["Messages"][0]
    receipt_handle = message["ReceiptHandle"]

    try:
        send_to_teams(message)
    except pymsteams.TeamsWebhookException as ex:
        print(ex)
        return

    sqs.delete_message(
        QueueUrl=queue,
        ReceiptHandle=receipt_handle
    )

def send_to_teams(message):
    print("Sending...")
    outgoing = pymsteams.connectorcard(teams)
    message_json = json.loads(message["Body"])
    priority = message_json['priority'].capitalize()
    body: str = message_json['message']
    body = body.replace("\n", "<br>")
    outgoing.text(f"<h1 style='font-weight: bold'>{priority} priority: {message_json['title']}</h1>"
                  f"<p>{body}</p>")
    outgoing.send()

if __name__ == "__main__":
    run = True
    while True:
        get_from_queue()
