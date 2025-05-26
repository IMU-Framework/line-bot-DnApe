
import requests, os
from format1_carousel import build_format1_carousel
from format2_carousel import build_format2_carousel
from utils.utils import get_text, fetch_notion_data, build_email_carousel, send_line_reply

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DB_ID = os.getenv('NOTION_DB_ID')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_REPLY_TOKEN = os.getenv('LINE_REPLY_TOKEN')

if __name__ == '__main__':
    data = fetch_notion_data()
    if data:
        for page in data:
            props = page['properties']
            format_type = get_text(props, 'Format')
            title = get_text(props, 'Title')
            if format_type == '逐句解析':
                flex_message = build_format1_carousel(props, title)
            elif format_type == '情境解析':
                flex_message = build_format2_carousel(props, title)
            else:
                flex_message = build_email_carousel(data)
            send_line_reply(flex_message)
    else:
        print("No data found.")
