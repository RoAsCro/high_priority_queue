import boto3
import pytest
from requests.exceptions import MissingSchema

import teams
from moto import mock_aws

message_body = '{"priority": "high", "title": "message title", "message": "this is a message body"}'

def replacement_send(message):
    pass

@mock_aws
def test_get_message_deletes():
    mock_sqs = boto3.client("sqs", region_name='us-east-1')
    queue = mock_sqs.create_queue(QueueName="team")['QueueUrl']
    teams.sqs = mock_sqs
    teams.queue = queue
    mock_sqs.send_message(QueueUrl=queue,
                         DelaySeconds=0,
                         MessageBody=message_body)

    retrieved_message = teams.get_from_queue()

    assert retrieved_message is not None

