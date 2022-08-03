from datetime import date
import json
import logging
import os
import random
import re

from fuzzywuzzy import fuzz
import pyjokes
from slack_bolt.app.async_app import AsyncApp as Slack
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import yaml

from breezeway import AsyncApp as Breezeway


# TODO: Add brivo code to home screen


def get_file(filename):
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, filename)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s]: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(get_file("prvrbot.log"))
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)


def get_config(filename):
    if not os.path.exists(filename):
        logger.fatal(f"Could not load {filename}. Does not exist")
        raise Exception(f"Could not load {filename}. Does not exist")
    with open(get_file(filename), "r") as f:
        return yaml.safe_load(f)


config = get_config("config/config.yml")


slack = Slack(token=config["slack"]["bot-token"], name="PRVRbot")
breezeway = Breezeway(
    client_id=config["breezeway"]["client-id"], client_secret=config["breezeway"]["client-secret"],
    company_id=config["breezeway"]["company-id"], url=config["breezeway"]["url"])


@slack.action("none")
async def handle_some_action(ack):
    await ack()


@slack.event("app_home_opened")
async def update_home_tab(client, event):
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
                                      "NoiseAware\n- Generate projects in :breezeway:Breezeway for things like low "
                                      "batteries on doorknobs.\n- Notify the team about changes in the weather. "
                                      ":rain_cloud: Eg. Reminder to check pool cover pumps if it's going to rain.\n- "
                                      "Sky is the limit. "
                          }
                      }
                  ]
                  })

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@slack.event("team_join")
async def ask_for_introduction(event, say):
    """When a user joins the workspace, send a message in #general asking them to introduce themselves"""
    if config["slack"]["welcome-module"]["enabled"] and not event["user"]["is_bot"]:
        user_id = event["user"]["id"]
        logger.info(f"{user_id} joined!")
        text = f"Welcome to the PRVR team, <@{user_id}>! :tada:🎉 You can introduce yourself in this channel."
        await say(text=text, channel=config["slack"]["welcome-module"]["channel"])


@slack.shortcut("create_breezeway_task")
async def create_breezeway_task(ack, body, client):
    task_ack = asyncio.create_task(ack())
    if config["breezeway"]["enabled"] is False:
        await task_ack
        return

    private_metadata = {
        "channel": body["channel"]["id"],
        "reply-to": body["message"]["thread_ts"] if "thread_ts" in body["message"] else body["message"]["ts"],
        "react-to": body["message"]["ts"]
    }

    units = await breezeway.get_units()
    units = sorted(units, key=lambda k: k["name"])
    unit_options = []
    for unit in units:
        ...
        # option = {
        #     "text": {
        #         "type": "plain_text",
        #         "text": unit["name"],
        #         "emoji": True
        #     },
        #     "value": str(unit['id'])
        # }
        # unit_options.append(option)
    result = {"ratio": 0}
    for unit in units:
        weight = len(unit["name"]) * 0.007 + 1
        ratio = fuzz.partial_ratio(unit["name"].lower(), body["message"]["text"].lower()) * weight
        if ratio > result["ratio"]:
            result = {"name": unit["name"], "id": unit["id"], "ratio": ratio}

    unit_department_block = {
        "type": "actions",
        "elements": [
            # {
            #     "type": "static_select",
            #     "placeholder": {
            #         "type": "plain_text",
            #         "text": "Select Property",
            #         "emoji": False
            #     },
            #     "options": unit_options,
            #     "action_id": "unit"
            # },
            {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select Department",
                    "emoji": True
                },
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Maintenance",
                        "emoji": True
                    },
                    "value": "maintenance"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Cleaning",
                            "emoji": True
                        },
                        "value": "housekeeping"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Inspection",
                            "emoji": True
                        },
                        "value": "inspection"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Maintenance",
                            "emoji": True
                        },
                        "value": "maintenance"
                    }
                ],
                "action_id": "department"
            }
        ]
    }
    if result["ratio"] > 65:
        unit_department_block["elements"][0]["initial_option"] = {
            "text": {
                "type": "plain_text",
                "text": result["name"],
                "emoji": True
            },
            "value": str(result["id"])
        }

    title_block = {
        "type": "input",
        "label": {
            "type": "plain_text",
            "text": "Title",
            "emoji": True
        },
        "element": {
            "type": "plain_text_input",
            "action_id": "title"
        }
    }
    description_block = {
        "type": "input",
        "label": {
            "type": "plain_text",
            "text": "Description",
            "emoji": True
        },
        "element": {
            "type": "plain_text_input",
            "multiline": True,
            "action_id": "description",
            "initial_value": body["message"]["text"]
        }
    }
    due_date_block = {
        "type": "input",
        "block_id": "due_date",
        "label": {
            "type": "plain_text",
            "text": "Due on",
            "emoji": True
        },
        "element": {
            "type": "datepicker",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a date",
                "emoji": True
            },
            "initial_date": f"{date.today()}",
            "action_id": "due_date"
        }
    }

    people = await breezeway.get_people()
    people = sorted(people, key=lambda k: k['first_name'])
    people_options = []

    for person in people:
        option = {
            "text": {
                "type": "plain_text",
                "text": f"{person['first_name']} {person['last_name'][0]}.",
                "emoji": True
            },
            "value": f"{person['id']}"
        }
        people_options.append(option)

    assignees_block = {
        "type": "input",
        "label": {
            "type": "plain_text",
            "text": "Assignees",
            "emoji": True
        },
        "element": {
            "type": "multi_static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select options",
                "emoji": True
            },
            "options": people_options,
            "action_id": "assignees"
        }
    }

    blocks = [unit_department_block,
              title_block,
              description_block,
              due_date_block,
              assignees_block]

    modal = {
        "type": "modal",
        "callback_id": "breezeway_task",
        "submit": {
            "type": "plain_text",
            "text": "Create",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "title": {
            "type": "plain_text",
            "text": "New Breezeway task",
            "emoji": True
        },
        "blocks": blocks,
        "private_metadata": json.dumps(private_metadata)
    }

    await client.views_open(trigger_id=body["trigger_id"], view=modal)
    await task_ack


@slack.action("unit")
async def handle_action(ack):
    await ack()


@slack.action("department")
async def update_view(ack, body, client):
    await ack()
    info = {}
    for v in body["view"]["state"]["values"].values():
        info |= v

    blocks = body["view"]["blocks"]

    people = await breezeway.get_people()
    people = sorted(people, key=lambda k: k['first_name'])
    people_options = []

    for person in people:
        option = {
            "text": {
                "type": "plain_text",
                "text": f"{person['first_name']} {person['last_name'][0]}.",
                "emoji": True
            },
            "value": f"{person['id']}"
        }
        people_options.append(option)

    blocks[4] = {
        "type": "input",
        "label": {
            "type": "plain_text",
            "text": "Assignees",
            "emoji": True
        },
        "element": {
            "type": "multi_static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select options",
                "emoji": True
            },
            "options": people_options,
            "action_id": "assignees"
        }
    }

    modal = {
        "type": "modal",
        "callback_id": "breezeway_task",
        "submit": {
            "type": "plain_text",
            "text": "Create",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "title": {
            "type": "plain_text",
            "text": "Create a Breezeway task",
            "emoji": True
        },
        "blocks": blocks,
        "private_metadata": body["view"]["private_metadata"]
    }

    await client.views_update(trigger_id=body["trigger_id"], view=modal, view_id=body["view"]["id"])


@slack.view("breezeway_task")
async def breezeway_task_submission(ack, body, client):
    # TODO dont allow projects in past
    # TODO enforce property
    logger.info(f"Received view submission from {body['user']['username']}")
    metadata = json.loads(body["view"]["private_metadata"])

    info = {}
    for v in body["view"]["state"]["values"].values():
        info |= v

    unit_id = info["unit"]["selected_option"]["value"]
    department = info["department"]["selected_option"]["value"]
    title = info["title"]["value"]
    description = info["description"]["value"]
    due_date = info["due_date"]["selected_date"]
    assignees = [int(v["value"]) for v in info['assignees']['selected_options']]

    project = await breezeway.create_project(unit_id=unit_id, department=department, title=title,
                                             description=description,
                                             due_date=due_date, assignees=assignees)
    if "id" in project:  # Successfully made project
        await ack()
        blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{info['unit']['selected_option']['text']['text']}: {project['name']}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Open in Breezeway",
                    "emoji": False
                },
                "value": "none",
                "url": f"https://app.breezeway.io/task/{project['id']}",  # TODO Dynamic URL
                "action_id": "none"
            }
        }]
        await slack.client.chat_postMessage(token=config["slack"]["bot-token"], text=f"Project made\n{project['name']}",
                                            channel=metadata["channel"], thread_ts=metadata["reply-to"], blocks=blocks,
                                            icon_emoji=":breezeway:")
        await slack.client.reactions_add(token=config["slack"]["bot-token"], channel=metadata["channel"],
                                         timestamp=metadata["react-to"], name="breezeway")
        # TODO add delete project button?

    else:
        await ack()
        await slack.client.chat_postEphemeral(config["slack"]["bot-token"], text=f"Something went wrong. Please try "
                                              "again or make build project in breezeway", channel=metadata["channel"],
                                              thread_ts=metadata["reply-to"], user=body["user"]["id"])


@slack.event("reaction_added")
async def handle_reaction_added_events():
    ...


@slack.event("reaction_removed")
async def handle_reaction_removed_events(body):
    logger.info(body)


# When a user says Hi in a DM, say Hi back
@slack.message(re.compile("^([Hh]i)|([Hh]ello)|([Hh]owdy)|(:wave:)"))
async def greet(message, say):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    user_id = message["user"]
    logger.info(f"{user_id} -> {slack.name}: {message['text']}")
    dm_channel = message["channel"]

    greeting = random.choice(["Hi!", "Hello.", "Howdy!", ":wave:"])
    await say(text=greeting, channel=dm_channel)
    logger.info(f"{slack.name} -> {user_id}: {greeting}")


# When a user says joke, send a joke
@slack.message(re.compile("^[jJ]oke$"))  # type: ignore
async def show_random_joke(message, say):
    channel_type = message["channel_type"]
    if channel_type != "im":
        return

    user_id = message["user"]
    logger.info(f"{user_id} -> {slack.name}: {message['text']}")
    dm_channel = message["channel"]

    # TODO make async or remove
    joke = pyjokes.get_joke("en", "all")
    logger.info(f"{slack.name} -> {user_id}: {joke}")

    await say(text=joke, channel=dm_channel)


@slack.event("message")
async def handle_message_events(body, ):
    logger.info(body)


async def main():
    handler = AsyncSocketModeHandler(app=slack, app_token=config["slack"]["app-token"])
    await breezeway.authenticate()
    await handler.start_async()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
