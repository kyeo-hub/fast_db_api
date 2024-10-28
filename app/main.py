from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# 配置模板目录
templates = Jinja2Templates(directory="templates")

# 初始化数据库
def init_db():
    conn = sqlite3.connect('sms.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sms (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# 在应用启动时初始化数据库
@app.on_event("startup")
def startup():
    init_db()

# 接收 SMS 信息的 Webhook
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        sender = data.get('sender')
        message = data.get('message')
        timestamp = data.get('timestamp')

        if not all([sender, message, timestamp]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        conn = sqlite3.connect('sms.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO sms (sender, message, timestamp) VALUES (?, ?, ?)''', (sender, message, timestamp))
        conn.commit()
        conn.close()

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 提供 Web 页面展示 SMS 信息
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = sqlite3.connect('sms.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM sms''')
    rows = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "sms_list": rows})

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)