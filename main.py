from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage
from module.format1_carousel import build_format1_carousel
from module.format2_carousel import build_format2_carousel
from utils.utils import fetch_notion_data, build_email_carousel
import os

app = Flask(__name__)

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
    if event.message.text == "外商email":
        notion_data = fetch_notion_data()
        flex_message = build_email_carousel(notion_data)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="外商Email解析", contents=flex_message))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"收到訊息: {event.message.text}"))