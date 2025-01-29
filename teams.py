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
    while run:
        response = sqs.receive_message(
            QueueUrl=queue,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"],
            VisibilityTimeout=0,
            WaitTimeSeconds=20
        )

        if "Messages" not in response:
            continue

        message = response["Messages"][0]
        receipt_handle = message["ReceiptHandle"]

        sqs.delete_message(
            QueueUrl=queue,
            ReceiptHandle=receipt_handle
        )
        send_to_teams(message)

def send_to_teams(message):
    outgoing = pymsteams.connectorcard(teams)
    message_json = json.loads(message["Body"])
    outgoing.text(f"{message_json['priority']} priority: {message_json['title']}\n"
                  f"{message_json['message']}")
    outgoing.send()

if __name__ == "__main__":
    run = True
    thread = Thread(target = get_from_queue)
    thread.start()
    while True:
        input1 = input()
        if input1 == "close":
            run = False
            break
