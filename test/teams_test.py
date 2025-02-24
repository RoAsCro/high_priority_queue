import threading
import time

import boto3
import pytest
from sqs_consumer.abstract_consumer import AbstractConsumer

import teams
from moto import mock_aws

class ConsumerStub(AbstractConsumer):
    @mock_aws()
    def __init__(self):
        super().__init__()

    def send(self, message):
        global received_message
        received_message = message["Body"]
        consumer.running = False

consumer = ConsumerStub()

message_body = '{"priority": "high", "title": "message title", "message": "this is a message body"}'
received_message = None

@mock_aws
def test_get_message():
    prepare_aws()
    consumer.sqs.send_message(QueueUrl=consumer.queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = consumer.get_from_queue()

    assert retrieved_message is not None

@mock_aws
def test_delete_message():
    prepare_aws()
    consumer.sqs.send_message(QueueUrl=consumer.queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = consumer.get_from_queue()
    consumer.delete(retrieved_message)

    assert "Message" not in consumer.sqs.receive_message(
        QueueUrl=consumer.queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

@mock_aws
def test_no_message():
    prepare_aws()
    retrieved_message = consumer.get_from_queue()
    assert retrieved_message is None


@mock_aws
def test_process_without_teams():
    prepare_aws()
    consumer.sqs.send_message(QueueUrl=consumer.queue,
                        DelaySeconds=0,
                        MessageBody=message_body)
    timer_thread = threading.Thread(target=timer, args=[5]) # Ensure test doesn't run forever if it fails
    timer_thread.start()
    consumer.running = True
    consumer.process()
    consumer.running = False
    global received_message
    assert (received_message is not None # Message was received
            and "Message" not in consumer.sqs.receive_message( # Message was deleted
        QueueUrl=consumer.queue,
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    ))

def timer(seconds):
    time.sleep(seconds)
    consumer.running = False

@mock_aws
def prepare_aws():
    mock_sqs = boto3.client("sqs", region_name='us-east-1')
    queue = mock_sqs.create_queue(QueueName="team")['QueueUrl']
    consumer.sqs = mock_sqs
    consumer.queue = queue
    return mock_sqs, queue

@pytest.fixture(autouse=True)
def before_each():
    global received_message
    received_message = None