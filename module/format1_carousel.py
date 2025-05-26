
from utils.utils import get_text, create_paragraph_block, create_list_block, create_footer, create_question_bubble

def build_format1_carousel(props, title):
    paragraphs = [get_text(props, f'Paragraph{i}') for i in range(1, 5)]
    labels = [get_text(props, f'Label{i}') for i in range(1, 5)]
    explanations = [get_text(props, f'Explanation{i}') for i in range(1, 5)]
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
                    {"type": "text", "text": "▼ 逐句解析", "size": "sm", "weight": "bold"},
                    create_paragraph_block(paragraphs[0], labels[0], explanations[0]),
                    create_paragraph_block(paragraphs[1], labels[1], explanations[1]),
                    *[create_list_block(lst) for lst in common_lists]
                ]},
                "footer": create_footer("試著回答 ▶")
            },
            create_question_bubble(questions)
        ]
    }
