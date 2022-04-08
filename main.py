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

    joke = pyjokes.get_joke("en", "all")
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
                            "text": "*Welcome to PRVRbot* :tada:\n\n*What are you?*\nI am a project started by Anthony. The PRVRbot project is still in its infancy. Currently, the main goal is for me to learn to aid people in day to day tasks by providing information when prompted by the user. In time, these passive abilities may be able to turn into tasks that I can do without needing to be prompted.\n\n*What can PRVRbot do right now?*\nWell, not much. PRVRbot is still in its infancy. but here is a list of what it can currently do...\n- Automatically welcome new PRVR members in #general\n- Tell you a dumb joke. Send me a DM saying \"joke\".\n\n*What do you think you will do in the future?*\nHere are some ideas...\n- Generate weekly Kaba lockout codes and hand them out as needed while keeping a log of who had access to them.\n- Send alerts from Noiseaware\n- Generate projects in Breezeway for things like low batteries on doorknobs.\n- Notify the team about changes in the weather. Eg. Reminder to check pool cover pumps if it's going to rain.\n- Sky is the limit.\n\nhttps://github.com/FastQuack/PRVRbot"
                        }
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
