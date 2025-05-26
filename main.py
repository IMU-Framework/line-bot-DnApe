from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage
from module.format1_carousel import build_format1_carousel
from module.format2_carousel import build_format2_carousel
from utils.utils import fetch_notion_data, build_email_carousel
import os

app = Flask(__name__)

# 使用 V2/V3 兼容初始化方式
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    print(f"Received LINE message: {text}")
    if text == "外商email":
        try:
            print("Fetching Notion data...")
            notion_data = fetch_notion_data()
            if not notion_data:
                print("No data fetched from Notion.")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="查無資料，請確認Notion內容"))
            else:
                print(f"Notion data fetched: {notion_data}")
                flex_message = build_email_carousel(notion_data)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="外商Email解析", contents=flex_message))
                print("Successfully sent Flex message")
        except Exception as e:
            print(f"Error in processing '外商email': {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="系統錯誤，請稍後再試"))
    else:
        print("Replying with simple text message")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"收到訊息: {text}"))
