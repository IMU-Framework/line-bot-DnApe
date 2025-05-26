
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
import os
from utils.utils import fetch_notion_data, build_email_carousel

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == "外商email":
        notion_data = fetch_notion_data()
        if notion_data:
            flex_message = build_email_carousel(notion_data)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="外商Email解析", contents=flex_message))
        else:
            line_bot_api.reply_message(event.reply_token, TextMessage(text="查無資料，請確認Notion內容"))
    else:
        line_bot_api.reply_message(event.reply_token, TextMessage(text=f"你說的是: {text}"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
