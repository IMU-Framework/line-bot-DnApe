
from utils.utils import get_text, create_explanation_block, create_list_block, create_footer, create_question_bubble

def build_format2_carousel(props, title):
    explanation1 = get_text(props, 'Explanation1')
    common_lists = [get_text(props, f'List{i}') for i in range(1, 4)]
    questions = [get_text(props, f'Question{i}') for i in range(1, 3)]
    
    return {
        "type": "carousel",
        "contents": [
            {
                "type": "bubble",
                "size": "mega",
                "header": {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": title, "color": "#ffffff", "size": "lg", "weight": "bold"}
                ], "backgroundColor": "#17406D"},
                "body": {"type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": "▼ 情境解析", "size": "sm", "weight": "bold"},
                    create_explanation_block(explanation1),
                    *[create_list_block(lst) for lst in common_lists]
                ]},
                "footer": create_footer("試著回答 ▶")
            },
            create_question_bubble(questions)
        ]
    }
