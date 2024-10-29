from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime
import sqlite3
import os
import logging

# 配置日志
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 配置模板目录
templates = Jinja2Templates(directory="templates")


# 初始化数据库
def init_db():
    try:
        conn = sqlite3.connect("sms.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS sms (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp TEXT, time TEXT)"""
        )
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# 转换时间
def convert_timestamp(timestamp):
    try:
        timestamp = int(timestamp)
        timestamp = timestamp / 1000
        timestamp = datetime.datetime.fromtimestamp(timestamp)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return timestamp_str
    except Exception as e:
        logger.error(f"Failed to convert timestamp: {e}")
        return "Invalid timestamp"


# 在应用启动时初始化数据库
@app.on_event("startup")
def startup():
    init_db()


# 接收 SMS 信息的 Webhook
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        sender = data.get("sender")
        message = data.get("message")
        timestamp = data.get("timestamp")

        if not all([sender, message, timestamp]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        if timestamp:
            # 转换时间戳
            time = convert_timestamp(timestamp)
        else:
            time = "No timestamp found"

        conn = sqlite3.connect("sms.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO sms (sender, message, timestamp, time) VALUES (?, ?, ?, ?)""",
            (sender, message, timestamp, time),
        )
        conn.commit()
        conn.close()
        logger.info("SMS received and stored successfully.")
        return {"status": "success"}
    except HTTPException as he:
        logger.error(f"HTTPException: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 提供 Web 页面展示 SMS 信息
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        conn = sqlite3.connect("sms.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM sms""")
        rows = cursor.fetchall()
        conn.close()
        logger.info("Fetched SMS list successfully.")
        return templates.TemplateResponse(
            "index.html", {"request": request, "sms_list": rows}
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)