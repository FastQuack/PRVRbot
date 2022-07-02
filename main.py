import os
import random
import re

import pyjokes
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
WELCOME_CHANNEL_ID = os.environ["WELCOME_CHANNEL_ID"]

app = AsyncApp(token=SLACK_BOT_TOKEN, name="PRVRbot")


@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    user_id = event["user"]
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        await client.views_publish(
            # the user that opened your app's app home
            user_id=user_id,
            # the view object that appears in the app home
            view={"type": "home", "callback_id": "home_view",

                  # body of the view
                  "blocks": [
                      {
                          "type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": ":wave: Howdy! I'm PRVRbot"
                          }
                      },
                      {
                          "type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": "What am I?"
                          }
                      },
                      {
                          "type": "divider"
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": "I am a project started by Anthony. I want to learn to aid people in day to day "
                                      "tasks by providing information when prompted. In time, these passive abilities "
                                      "may be able to turn into tasks that I can do without needing to be prompted. "
                          }
                      },
                      {
                          "type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": "What can I do right now?"
                          }
                      },
                      {
                          "type": "divider"
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": "Well, not much. I am still in my infancy, but here is a list of what I can "
                                      "currently do...\n  - Automatically welcome new PRVR members in #general\n  - "
                                      "Tell you a dumb joke. Send me a DM saying \"joke\". "
                          }
                      },
                      {
                          "type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": "What do I think I will do in the future?"
                          }
                      },
                      {
                          "type": "divider"
                      },
                      {
                          "type": "section",
                          "text": {
                              "type": "mrkdwn",
                              "text": "- Generate weekly :key: lockout codes and hand them out as needed while "
                                      "keeping a log of who had access to them.\n- Send alerts from :ear: "
                                      "Noiseaware\n- Generate projects in :breezeway:Breezeway for things like low "
                                      "batteries on doorknobs.\n- Notify the team about changes in the weather. "
                                      ":rain_cloud: Eg. Reminder to check pool cover pumps if it's going to rain.\n- "
                                      "Sky is the limit. "
                          }
                      }
                  ]
                  })

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


# When a user joins the workspace, send a message in #general asking them to introduce themselves
@app.event("team_join")
async def ask_for_introduction(event, say):
    user_id = event["user"]["id"]
    text = f"Welcome to the PRVR team, <@{user_id}>! :tada:🎉 You can introduce yourself in this channel."
    await say(text=text, channel=WELCOME_CHANNEL_ID)


# When a user says Hi in a DM, say Hi back
@app.message(re.compile("^([Hh]i)|([Hh]ello)|([Hh]owdy)|(:wave:)"))
async def greet(message, say, logger):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    greeting = random.choice(["Hi!", "Hello.", "Howdy!", ":wave:"])
    logger.info(f"Greeted user {user_id}")
    await say(text=greeting, channel=dm_channel)


# When a user says joke, send a joke
@app.message(re.compile("^[jJ]oke$"))  # type: ignore
async def show_random_joke(message, say, logger):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    # TODO make async or remove
    joke = pyjokes.get_joke("en", "all")
    logger.info(f"Sent joke < {joke} > to user {user_id}")

    await say(text=joke, channel=dm_channel)


async def main():
    handler = AsyncSocketModeHandler(app=app, app_token=SLACK_APP_TOKEN)
    slack_handler = asyncio.create_task(handler.start_async())
    await slack_handler


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
