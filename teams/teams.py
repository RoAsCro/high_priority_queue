import json
import os

import pymsteams

from dotenv import load_dotenv

from abstract_comsumer import AbstractConsumer

load_dotenv()
class TeamsConsumer(AbstractConsumer):
    teams_webhook = os.getenv("TEAMS_WEBHOOK")
    exception = pymsteams.TeamsWebhookException
    def send(self, message_to_send):
        print("Sending...")
        outgoing = pymsteams.connectorcard(self.teams_webhook)
        message_json = json.loads(message_to_send["Body"])
        priority = message_json['priority'].capitalize()
        body: str = message_json['message']
        body = body.replace("\n", "<br>")
        outgoing.text(f"<h1 style='font-weight: bold'>{priority} priority: {message_json['title']}</h1>"
                      f"<p>{body}</p>")
        outgoing.send()


def run():
    TeamsConsumer().run()

if __name__ == "__main__":
    run()
