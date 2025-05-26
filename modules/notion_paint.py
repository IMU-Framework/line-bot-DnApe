import os
import requests
import colorsys

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_PAINT_TABLE_DB")

def fetch_notion_paint_data():
    """
    從 Notion 資料庫獲取油漆資料
    
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

def is_light_color(hex_color):
    """
    判斷顏色是否為淺色
    
    Args:
        hex_color: 十六進制顏色代碼 (如 '#FFFFFF')
        
    Returns:
        bool: 如果是淺色返回 True，否則返回 False
    """
    # 移除 # 號並轉換為 RGB
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:  # 處理簡寫形式 (#RGB)
        hex_color = ''.join([c*2 for c in hex_color])
    
    try:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    except ValueError:
        return False  # 如果顏色代碼無效，預設為深色
    
    # 轉換為 HSL 並判斷亮度
    r, g, b = r/255.0, g/255.0, b/255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    # 亮度大於 0.6 視為淺色
    return l > 0.6

def build_paint_table_flex():
    """
    構建油漆表格的 Flex Message
    
    Returns:
        dict: LINE Flex Message 格式的輪播卡片
    """
    notion_rows = fetch_notion_paint_data()
    
    # 處理排序
    sorted_rows = []
    for row in notion_rows:
        props = row["properties"]
        # 獲取 Order 欄位，如果不存在或為空則設為 999（排在最後）
        order_value = 999
        if "Order" in props:
            order_prop = props["Order"]
            if "number" in order_prop and order_prop["number"] is not None:
                order_value = order_prop["number"]
        
        sorted_rows.append((order_value, row))
    
    # 按 Order 排序
    sorted_rows.sort(key=lambda x: x[0])
    sorted_notion_rows = [row for _, row in sorted_rows]

    bubbles = []
    for row in sorted_notion_rows:
        props = row["properties"]

        # 設定預設/空白/fallback值，確保即使資料庫欄位缺失也能正常顯示
        title = get_text(props.get("Title", {}).get("title", [])) or "未命名"
        name = get_text(props.get("Name", {}).get("rich_text", [])) or "unnamed"
        site1 = get_text(props.get("Site1", {}).get("rich_text", [])) or "-"
        site2 = get_text(props.get("Site2", {}).get("rich_text", [])) or "-"
        site3 = get_text(props.get("Site3", {}).get("rich_text", [])) or "-"
        brand = get_text(props.get("Brand", {}).get("rich_text", [])) or "品牌未定"
        color_number = get_text(props.get("ColorNumber", {}).get("rich_text", [])) or "色號未定"
        color_code = get_text(props.get("ColorCode", {}).get("rich_text", [])) or "#CCCCCC"  # 預設灰色

        # 判斷文字顏色
        text_color = "#000000" if is_light_color(color_code) else "#ffffff"

        # URI 處理 - 如果為空則完全禁用按鈕
        uri = props.get("uri", {}).get("url", "")
        button_disabled = not bool(uri)  # 如果 uri 為空則禁用按鈕
        if not uri:
            # 當 URI 為空時，回傳postback
            footer_content = {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                      "type": "postback",
                      "label": color_number,
                      "data": "user requests for detail"
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
                    "label": color_number,
                    "uri": uri
                },
            }

        bubble = {
            "type": "bubble",
            "size": "micro",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "color": text_color,  # 根據背景色自動調整文字顏色
                        "align": "start",
                        "size": "xl",
                        "gravity": "center",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": name,
                        "color": text_color,  # 根據背景色自動調整文字顏色
                        "align": "start",
                        "size": "lg",
                        "gravity": "center",
                        "margin": "lg"
                    }
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
                "contents": [
                    # site1
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置1",
                                "flex": 1,
                                "size": "sm",
                                "color": "#8C8C8C"
                                # "wrap": True,
                            },
                            {
                                "type": "text",
                                "text": site1,
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666"
                            }
                        ]
                    },
                    # site2
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置2",
                                "flex": 1,
                                "size": "sm",
                                "color": "#8C8C8C"
                            },
                            {
                                "type": "text",
                                "text": site2,
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666"
                            }
                        ]
                    },
                    # site3
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "位置3",
                                "flex": 1,
                                "size": "sm",
                                "color": "#8C8C8C"
                            },
                            {
                                "type": "text",
                                "text": site3,
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": brand,
                        "align": "center",
                        "weight": "bold"
                    },
                    footer_content
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": color_code,
                    # "height": "120px"
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

