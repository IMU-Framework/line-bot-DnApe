from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage, PostbackEvent
from module.format1_carousel import build_format1_carousel
from module.format2_carousel import build_format2_carousel
from utils.utils import fetch_notion_data, build_email_carousel, get_text
import os
import traceback

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print(f"Webhook received with body: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid Signature Error")
        abort(400)
    except Exception as e:
        print(f"Exception during webhook handling: {e}")
        print(traceback.format_exc())
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        text = event.message.text
        print(f"Received LINE message: {text}")
        if text == "外商email":
            print("Fetching Notion data...")
            notion_data = fetch_notion_data()
            if not notion_data:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="查無資料"))
            else:
                carousels = build_email_carousel(notion_data)
                for carousel in carousels:
                    line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="外商Email解析", contents=carousel))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"收到訊息: {text}"))
    except Exception as e:
        print(f"Exception in handle_message: {e}")
        print(traceback.format_exc())

@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = event.postback.data
        print(f"Received postback data: {data}")
        notion_data = fetch_notion_data()
        target_page = next((page for page in notion_data if get_text(page['properties'], 'ButtonData', formula=True) == data), None)
        if target_page:
            format_type = get_text(target_page['properties'], 'Format')
            title = get_text(target_page['properties'], 'Title')
            if format_type == "逐句解析":
                flex_message = build_format1_carousel(target_page['properties'], title)
            elif format_type == "情境解析":
                flex_message = build_format2_carousel(target_page['properties'], title)
            else:
                flex_message = {"type": "text", "text": "無法辨識格式"}
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text=title, contents=flex_message))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到對應資料"))
    except Exception as e:
        print(f"Exception in handle_postback: {e}")
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="系統錯誤"))

@app.route('/', methods=['GET'])
def index():
    return 'Service is running.'
