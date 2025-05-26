import requests, os

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DB_ID = os.getenv('NOTION_DB_ID')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_REPLY_TOKEN = os.getenv('LINE_REPLY_TOKEN')

def get_text(props, key, formula=False):
    if formula:
        return props.get(key, {}).get('formula', {}).get('string', ' ')
    return props.get(key, {}).get('rich_text', [{}])[0].get('plain_text', ' ') if props.get(key, {}).get('rich_text') else ' '

def create_paragraph_block(paragraph, label, explanation):
    return {
        "type": "box", "layout": "vertical", "contents": [
            {"type": "box", "layout": "horizontal", "contents": [
                {"type": "box", "layout": "vertical", "contents": [], "borderWidth": "medium", "borderColor": "#BCC3CC", "width": "1px", "cornerRadius": "lg", "backgroundColor": "#BCC3CC"},
                {"type": "text", "text": paragraph, "wrap": True, "size": "lg", "margin": "lg"}
            ], "margin": "lg"},
            {"type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": label, "flex": 1, "color": "#8d8d8d"},
                {"type": "separator", "color": "#8d8d8d"},
                {"type": "text", "text": explanation, "margin": "lg", "flex": 4, "wrap": True}
            ], "margin": "md"}
        ]
    }

def create_explanation_block(explanation):
    return {
        "type": "box", "layout": "horizontal", "contents": [
            {"type": "box", "layout": "vertical", "contents": [], "borderWidth": "medium", "borderColor": "#BCC3CC", "width": "1px", "cornerRadius": "lg", "backgroundColor": "#BCC3CC"},
            {"type": "text", "text": explanation, "wrap": True, "size": "lg", "margin": "lg"}
        ], "margin": "lg"
    }

def create_list_block(text):
    return {
        "type": "box", "layout": "horizontal", "contents": [
            {"type": "box", "layout": "vertical", "contents": [], "flex": 1},
            {"type": "box", "layout": "vertical", "contents": [], "width": "10px", "height": "10px", "backgroundColor": "#BCC3CC", "margin": "sm", "cornerRadius": "md", "flex": 2},
            {"type": "text", "text": text, "wrap": True, "size": "sm", "flex": 40, "margin": "md"}
        ], "spacing": "none", "margin": "sm"
    }

def create_footer(text):
    return {"type": "box", "layout": "horizontal", "contents": [
        {"type": "text", "text": text, "color": "#ffffff", "size": "sm", "align": "end", "gravity": "center"}
    ], "height": "44px", "backgroundColor": "#17406D"}

def create_question_bubble(questions):
    return {
        "type": "bubble", "size": "mega",
        "body": {"type": "box", "layout": "vertical", "contents": [
            {"type": "text", "text": "▼ 試著回答", "size": "sm", "weight": "bold"},
            *[{"type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"Q{i+1}", "flex": 1, "color": "#8d8d8d"},
                {"type": "separator", "color": "#8d8d8d"},
                {"type": "text", "text": q, "margin": "lg", "flex": 6, "wrap": True}
            ], "margin": "md"} for i, q in enumerate(questions)]
        ]}, "footer": create_footer("DigNo Ape")}

def fetch_notion_data():
    url = f'https://api.notion.com/v1/databases/{DB_ID}/query'
    headers = {'Authorization': f'Bearer {NOTION_TOKEN}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
    body = {"filter": {"property": "Posted", "checkbox": {"equals": True}}, "page_size": 12}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        print("Notion API Error:", response.text)
        return []
    return response.json().get('results', [])

def build_email_carousel(data):
    bubbles = []
    for idx, page in enumerate(data, start=1):
        props = page['properties']
        title = get_text(props, 'Title')
        email_content = get_text(props, 'EmailContent')
        button_data = get_text(props, 'ButtonData', formula=True)
        bubble = {
            "type": "bubble", "size": "mega",
            "header": {"type": "box", "layout": "horizontal", "contents": [
                {"type": "text", "text": f"#{idx}", "flex": 2, "color": "#ffffff", "size": "lg"},
                {"type": "text", "text": title, "color": "#ffffff", "size": "lg", "weight": "bold", "flex": 8}
            ], "backgroundColor": "#17406D"},
            "body": {"type": "box", "layout": "vertical", "contents": [
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "box", "layout": "vertical", "contents": [], "borderWidth": "medium", "borderColor": "#BCC3CC", "width": "1px", "cornerRadius": "lg", "backgroundColor": "#BCC3CC"},
                    {"type": "text", "text": email_content, "wrap": True, "size": "xs", "margin": "lg"}
                ]}, {"type": "separator", "margin": "lg", "color": "#DDE7F2"}
            ]},
            "footer": {"type": "box", "layout": "horizontal", "contents": [
                {"type": "button", "action": {"type": "postback", "label": "看解析", "data": button_data}, "style": "primary", "height": "sm"}
            ], "backgroundColor": "#17406D"},
            "styles": {"body": {"backgroundColor": "#DDE7F2"}}
        }
        bubbles.append(bubble)
    return {"type": "carousel", "contents": bubbles}
