import threading
import time

import boto3
import pytest

from teams import TeamsConsumer
from moto import mock_aws

teams_consumer = TeamsConsumer()

default_teams_method  = teams_consumer.send

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

    retrieved_message = teams_consumer.get_from_queue()

    assert retrieved_message is not None

@mock_aws
def test_delete_message():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    mock_sqs.send_message(QueueUrl=queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = teams_consumer.get_from_queue()
    teams_consumer.delete(retrieved_message)

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

    retrieved_message = teams_consumer.get_from_queue()

    assert retrieved_message is None


@mock_aws
def test_run_without_teams():
    sqs = prepare_aws()
    mock_sqs = sqs[0]
    queue = sqs[1]
    teams_consumer.send = send_to_teams_stub
    mock_sqs.send_message(QueueUrl=queue,
                        DelaySeconds=0,
                        MessageBody=message_body)
    timer_thread = threading.Thread(target=timer, args=[10]) # Ensure test doesn't run forever if it fails
    timer_thread.start()
    teams_consumer.run()


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
    teams_consumer.sqs = mock_sqs
    teams_consumer.queue = queue
    return mock_sqs, queue

def timer(seconds):
    time.sleep(seconds)
    teams_consumer.running = False

def send_to_teams_stub(message):
    global received_message
    received_message = message["Body"]
    teams_consumer.running = False

@pytest.fixture(autouse=True)
def before_each():
    teams_consumer.send = default_teams_method
    global received_message
    received_message = None