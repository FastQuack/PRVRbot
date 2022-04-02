import logging
import os
import re

import pyjokes

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = App(token=SLACK_BOT_TOKEN, name="PRVRbot")
logger = logging.getLogger(__name__)


@app.message(re.compile("^joke$"))  # type: ignore
def show_random_joke(message, say):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    joke = pyjokes.get_joke()
    logger.info(f"Sent joke < {joke} > to user {user_id}")

    say(text=joke, channel=dm_channel)


# When a user joins the workspace, send a message in #general asking them to introduce themselves
@app.event("team-join")
def ask_for_introduction(event, say):
    welcome_channel_id = "C31PR67DX"  # general
    user_id = event["user"]
    text = f"Welcome to the PRVR team, <@{user_id}>! :tada:🎉 You can introduce yourself in this channel."
    say(text=text, channel=welcome_channel_id)


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to :prvr:PRVRbot's home* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "want to hear a joke?"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Get Joke!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
