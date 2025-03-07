import json
import os

import pymsteams
from dotenv import load_dotenv
from sqs_consumer import abstract_consumer

load_dotenv()
teams_webhook = os.getenv("TEAMS_WEBHOOK")
exception = pymsteams.TeamsWebhookException
class TeamsConsumer(abstract_consumer.AbstractConsumer):
    def __init__(self):
        super().__init__(queue_var_name="HIGH_PRIORITY_QUEUE")
        self.exception = exception
        self.outgoing = pymsteams.connectorcard(teams_webhook)


    def send(self, message_to_send):
        message_json = json.loads(message_to_send["Body"])
        priority = message_json['priority'].capitalize()
        body: str = message_json['message']
        body = body.replace("\n", "<br>")
        self.outgoing.text(f"<h1 style='font-weight: bold'>{priority} priority: {message_json['title']}</h1>"
                      f"<p>{body}</p>")
        self.outgoing.send()

consumer = TeamsConsumer()

run = consumer.run

if __name__ == "__main__":
    try:
        run().run(host="0.0.0.0")
    except KeyboardInterrupt:
        consumer.info_logger.info("Shutting Down...")
        consumer.bg_thread.join()
        consumer.running = False
