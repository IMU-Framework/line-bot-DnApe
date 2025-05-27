from flask import Flask, request, abort
import os
import json

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer
)

from modules.notion_paint import build_paint_table_flex
from modules.notion_EmailCards import build_email_table_flex

app = Flask(__name__)

# 讀取環境變數
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    
    with ApiClient(configuration) as api_client:
        api = MessagingApi(api_client)
        
        # 根據 data 的值來決定回應內容
        if data.startswith("view_detail:"):  # 修改這裡以匹配按鈕中的數據格式
            detail_id = data.split(":", 1)[1] if ":" in data else "default"
            
            # 這裡可以根據 detail_id 查詢不同的解析內容
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"這是關於 {detail_id} 的詳細解析內容...")]
                )
            )
        # 為了向後兼容，保留原來的處理方式
        elif data.startswith("user requests for detail"):
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這是詳細解析內容...")]
                )
            )

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
                        text="請輸入下列指令之一：\n- 外商email or 商務英文\n- 油漆色號\n- 企業識別 or CIS"
                    )]
                )
            )

        elif text in ["外商email", "商務英文"]:
            try:
                flex = build_email_table_flex()
                print("✅ Email範例輸出：", json.dumps(flex, ensure_ascii=False, indent=2))  # DEBUG
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(
                            alt_text="外商email",
                            contents=FlexContainer.from_dict(flex)
                        )]
                    )
                )
            except Exception as e:
                print("❌ 發送Email卡片失敗：", e) 
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="⚠️ Email卡片讀取失敗，請稍後再試")]
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
            try:
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
            except Exception as e:
                print("❌ 發送企業識別色卡失敗：", e)
                api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="⚠️ 企業識別色卡讀取失敗，請稍後再試")]
                    )
                )

        else:
            return  # 不回應未指定指令

if __name__ == "__main__":
    # 本地開發時使用
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
