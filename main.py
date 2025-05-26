from flask import Flask, request, abort
import os
import json

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
)

from modules.notion_paint import build_paint_table_flex

app = Flask(__name__)

# 讀取環境變數
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip().lower()
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)

        if text == "其他查詢":
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請輸入下列指令之一：\n- 油漆色號\n- 企業識別 or CIS"
                    )]
                )
            )

        elif text in ["油漆色號", "油漆色卡", "油漆"]:
            try:
                flex = build_paint_table_flex()
                print("✅ Flex JSON 輸出：", json.dumps(flex, ensure_ascii=False, indent=2))  # DEBUG
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(
                            alt_text="油漆色卡",
                            contents=FlexContainer.from_dict(flex)
                        )]
                    )
                )
            except Exception as e:
                print("❌ 發送色卡失敗：", e) 
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="⚠️ 色卡讀取失敗，請稍後再試")]
                    )
                )

        elif text in ["企業識別", "cis"]:
            with open("flex_templates/cis.json", "r", encoding="utf-8") as f:
                cis_flex = json.load(f)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(
                        alt_text="企業識別色卡",
                        contents=FlexContainer.from_dict(cis_flex)
                    )]
                )
            )

        else:
            return  # 不回應未指定指令
