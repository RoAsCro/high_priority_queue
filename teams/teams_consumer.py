import json
import os

import dotenv
import pymsteams
from dotenv import load_dotenv
from flask import Flask
import logging

import sqs_consumer


load_dotenv()
teams_webhook = os.getenv("TEAMS_WEBHOOK")

exception = pymsteams.TeamsWebhookException
consumer = sqs_consumer.abstract_consumer.AbstractConsumer(dotenv.dotenv_values())


def send(message_to_send):
    logging.info("Sending...")
    outgoing = pymsteams.connectorcard(teams_webhook)
    message_json = json.loads(message_to_send["Body"])
    priority = message_json['priority'].capitalize()
    body: str = message_json['message']
    body = body.replace("\n", "<br>")
    outgoing.text(f"<h1 style='font-weight: bold'>{priority} priority: {message_json['title']}</h1>"
                  f"<p>{body}</p>")
    outgoing.send()


consumer.send = send
consumer.exception = exception
bg_thread = consumer.background_thread()
def run():
    health_checker = Flask(__name__)
    health_checker.register_blueprint(consumer.router)
    return health_checker

if __name__ == "__main__":
    print(dotenv.dotenv_values())
    print(consumer.queue)

    try:
        run().run(host="0.0.0.0")
    except KeyboardInterrupt:
        logging.info("Shutting Down...")
        bg_thread.join()
        consumer.running = False
