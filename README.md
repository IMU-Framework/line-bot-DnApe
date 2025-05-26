```
line-bot-opms/
│
├── main.py                   # 主程式
├── .python-version           # 指定Python版本 (optional)
├── Procfile                  # Gunicorn啟動指令 (for Render)
├── render.yaml               # Render自動部署設定 (for Render)
├── requirements.txt          # 相依套件清單
│
├── templates/                # 靜態 Flex Message 模板
│   ├── cis.json              # 企業識別色卡
│   └── paint.json            # 油漆色號
│
└── modules/                  # 動態 Flex Message fetching Notion DB
    └── notion_paint.py       # 產生油漆色卡 .json
```
