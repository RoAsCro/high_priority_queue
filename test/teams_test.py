import threading
import time

import boto3
import pytest

import teams
from moto import mock_aws

default_teams_method  = teams.send_to_teams

message_body = '{"priority": "high", "title": "message title", "message": "this is a message body"}'
received_message = None

def replacement_send(message):
    pass

@mock_aws
def test_get_message():
    sqs = prepare_aws()
    sqs[0].send_message(QueueUrl=sqs[1],
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = teams.get_from_queue()

    assert retrieved_message is not None

@mock_aws
def test_delete_message():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    mock_sqs.send_message(QueueUrl=queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = teams.get_from_queue()
    teams.delete(retrieved_message)

    assert "Message" not in mock_sqs.receive_message(
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    )

@mock_aws
def test_no_message():
    sqs = prepare_aws()

    retrieved_message = teams.get_from_queue()

    assert retrieved_message is None


@mock_aws
def test_run_without_teams():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    teams.send_to_teams = send_to_teams_stub
    mock_sqs.send_message(QueueUrl=queue,
                        DelaySeconds=0,
                        MessageBody=message_body)
    timer_thread = threading.Thread(target=timer, args=[10]) # Ensure test doesn't run forever if it fails
    timer_thread.start()
    teams.run()


    assert (received_message is not None # Message was received
            and "Message" not in mock_sqs.receive_message( # Message was deleted
        QueueUrl=queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=20
    ))

@mock_aws
def prepare_aws():
    mock_sqs = boto3.client("sqs", region_name='us-east-1')
    queue = mock_sqs.create_queue(QueueName="team")['QueueUrl']
    teams.sqs = mock_sqs
    teams.queue = queue
    return mock_sqs, queue

def timer(seconds):
    time.sleep(seconds)
    teams.running = False

def send_to_teams_stub(message):
    global received_message
    received_message = message["Body"]
    teams.running = False

@pytest.fixture(autouse=True)
def before_each():
    teams.send_to_teams = default_teams_method
    global received_message
    received_message = None