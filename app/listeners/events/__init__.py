import logging
import json

import slack_sdk
import slack_bolt

from app import app


@app.view("website-unblock-req")
def on_webstart_unblock_req(ack: slack_bolt.Ack, body: dict, client: slack_sdk.WebClient, logger: logging.Logger):
    ack()
    values = body["view"]["state"]["values"]
    logger.info("body=%s", json.dumps(values, ensure_ascii=False, indent=2))

    requestor = body["user"]["id"]

    p_reason = values["p_reason"]["input"]["value"]
    p_users = values["p_users"]["input"]["selected_users"]
    p_devices = {it["value"] for it in values["p_devices"]["input"]["selected_options"]}

    p_users = [client.users_info(user=it).data["user"] for it in p_users if it != "USLACKBOT"]
    p_users = [
        {"slack_id": it["id"], "name": it["name"], "email": it["profile"].get("email")}
        for it in p_users
        if not it.get("is_bot")
    ]

    logger.info("p_reason=%s", p_reason)
    logger.info("p_users=%s", p_users)
    logger.info("p_devices=%s", p_devices)


@app.action("start-resignation")
def start_resignation(ack: slack_bolt.Ack, body: dict, client: slack_sdk.WebClient, logger: logging.Logger):
    ack()
    logger.info("body=%s", json.dumps(body, ensure_ascii=False, indent=2))
    client.chat_postMessage(channel=body["user"]["id"], text=f"<@{body["user"]["id"]}>님, 퇴사 신청이 완료되었습니다.")


@app.action("start-website-unblock-req-form")
def start_website_unblock_req(ack: slack_bolt.Ack, body: dict, client: slack_sdk.WebClient, logger: logging.Logger):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "website-unblock-req",
            "title": {"type": "plain_text", "text": "웹사이트 접근 허용 신청", "emoji": True},
            "submit": {"type": "plain_text", "text": "신청", "emoji": True},
            "close": {"type": "plain_text", "text": "취소", "emoji": True},
            "blocks": [
                {
                    "block_id": "p_reason",
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "접근 허용이 필요하신 사유에 대해 간단히 기재해주세요.",
                        "emoji": True,
                    },
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "input",
                    },
                },
                {
                    "block_id": "p_users",
                    "type": "input",
                    "label": {"type": "plain_text", "text": "사용자들을 선택해주세요", "emoji": True},
                    "element": {
                        "type": "multi_users_select",
                        "action_id": "input",
                        "placeholder": {"type": "plain_text", "text": "Select users", "emoji": True},
                    },
                },
                {
                    "block_id": "p_devices",
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "사용하실 구간을 알려주세요 (ex : Local, VI, VD, VP)",
                        "emoji": True,
                    },
                    "element": {
                        "type": "multi_static_select",
                        "action_id": "input",
                        "placeholder": {"type": "plain_text", "text": "Select options", "emoji": True},
                        "options": [
                            {"text": {"type": "plain_text", "text": "Local", "emoji": True}, "value": "Local"},
                            {"text": {"type": "plain_text", "text": "VI", "emoji": True}, "value": "VI"},
                            {"text": {"type": "plain_text", "text": "VD", "emoji": True}, "value": "VD"},
                        ],
                    },
                },
            ],
        },
    )


@app.event("app_home_opened")
def app_home_opened_callback(client: slack_sdk.WebClient, event: dict, logger: logging.Logger):
    # ignore the app_home_opened event for anything but the Home tab
    if event["tab"] != "home":
        return

    try:
        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": "인프라보안팀 업무 신청", "emoji": True}},
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "웹사이트 접근 허용 신청.\n어쩌고 저쩌고 주절주절"},
                        "accessory": {
                            "type": "button",
                            "action_id": "start-website-unblock-req-form",
                            "text": {"type": "plain_text", "text": "신청"},
                        },
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "퇴사 신청"},
                        "accessory": {
                            "type": "button",
                            "action_id": "start-resignation",
                            "text": {"type": "plain_text", "text": "⚡️초고속 즉시 퇴사!", "emoji": True},
                        },
                    },
                ],
            },
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")
