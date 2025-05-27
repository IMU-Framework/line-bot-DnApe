import os
import requests

NOTION_TOKEN = os.getenv("NOTION_API_KEY_DNAPE")
NOTION_DATABASE_ID = os.getenv("NOTION_EMAIL_TABLE_DB")


def fetch_notion_email_data():
    """
    從 Notion 資料庫獲取email範例
    
    Returns:
        list: Notion 資料庫中的所有記錄
    """
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    return res.json().get("results", [])

def build_email_table_flex():
    """
    構建Email卡片的 Flex Message
    
    Returns:
        dict: LINE Flex Message 格式的輪播卡片
    """
    notion_rows = fetch_notion_email_data()
    
    # 處理排序
    sorted_rows = []
    for row in notion_rows:
        props = row.get("properties", {})
        # 預設排序值（排在最後）
        order_value = 999
        
        try:
            # 嘗試獲取 Order 欄位
            if "Order" in props:
                order_prop = props["Order"]
                if "number" in order_prop and order_prop["number"] is not None:
                    order_value = float(order_prop["number"])  # 轉換為數字以確保正確排序
        except Exception as e:
            print(f"排序處理時發生錯誤: {e}")
            # 發生錯誤時使用預設值
        
        sorted_rows.append((order_value, row))

    # 按 Order 排序
    sorted_rows.sort(key=lambda x: x[0])
    sorted_notion_rows = [row for _, row in sorted_rows]

    bubbles = []
    for row in sorted_notion_rows:
        props = row["properties"]

        # 取得欄位參數、設定預設/空白/fallback值
        ## 非序列化欄位
        posted = props.get("Posted", {}).get("checkbox", False)
        content_format = get_text(props.get("Format", {}).get("text", [])) or "Other"
        title = get_text(props.get("Title", {}).get("title", [])) or "未命名"
        content = get_text(props.get("EmailContent", {}).get("rich_text", [])) or "-"
        buttondata = props.get("ButtonData", {}).get("formula", {}).get("string", "")

        ## 序列化欄位配置處理
        item_configs = {
            "Explanation": 4,
            "Paragraph": 4,
            "Label": 4,
            "List": 4,
            "Question": 2
        }

        all_items = {}
        for item_type, count in item_configs.items():
            all_items[item_type.lower()] = [
                get_text(props.get(f"{item_type}{i}", {}).get("rich_text", [])) or "-" 
                for i in range(1, count+1)
            ]

        # 獲取列表項目
        list_items = all_items["list"]
        
        # URI 處理 - 如果為空則完全禁用按鈕
        uri = props.get("uri", {}).get("url", "")
        button_disabled = not bool(uri)  # 如果 uri 為空則禁用按鈕

        if not uri:
            footer_content = {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": "看解析",
                    "data": f"view_detail:{buttondata}" if buttondata else "view_detail:default",
                    "displayText": "正在查詢解析內容..."  # 這會在用戶點擊後顯示在聊天中
                }
            }
        else:
            # 當 URI 有值時，使用按鈕進行外部連結
            footer_content = {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "看解析",
                    "uri": uri
                },
            }

        # 構建 body 的 contents
        body_contents = [
            {
                "type": "text",
                "text": content,
                "color": "#000000",  #黑字
                "align": "start",
                "size": "sm",
                "gravity": "center",
                "margin": "lg",
                "wrap": True,
            }
        ]
        
        # 添加列表項目
        for i, list_item in enumerate(list_items[:3], 1):  # 只使用前3個
            if list_item != "-":  # 只添加非空項目
                body_contents.append({
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"位置{i}",
                            "flex": 1,
                            "size": "sm",
                            "color": "#8C8C8C"
                        },
                        {
                            "type": "text",
                            "text": list_item,
                            "flex": 2,
                            "size": "sm",
                            "color": "#666666"
                        }
                    ]
                })

        bubble = {
            "type": "bubble",
            "size": "micro",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": content_format,
                        "color": "#BFBFBF",  # 灰字
                        "align": "start",
                        "size": "xs",
                        "gravity": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": title,
                        "color": "#ffffff",  # 白字
                        "align": "start",
                        "size": "xl",
                        "gravity": "center",
                        "weight": "bold"
                    },
                ],
                "paddingTop": "19px",
                "paddingAll": "12px",
                "paddingBottom": "16px",
                "height": "150px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "paddingAll": "12px",
                "contents": body_contents
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    footer_content
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": "#17406D",  #數原藍
                },
                "footer": {
                    "separator": False
                }
            }
        }

        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles[:12]  # 設限卡片數量上限12
    }

def get_text(rich_items):
    """
    從 Notion 富文本欄位中提取純文本
    
    Args:
        rich_items: Notion 富文本欄位
        
    Returns:
        str: 提取的純文本
    """
    if not rich_items:
        return ""
    return "".join([r.get("plain_text", "") for r in rich_items])
