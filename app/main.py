from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import os

DATABASE_URL = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}".format(
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", ""),
    port=os.getenv("DB_PORT", "3306"),
    dbname=os.getenv("DB_NAME", "gallery"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost")
# 生命周期管理（连接池只创建一次）
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化连接池
    engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
    SessionLocal = sessionmaker(bind=engine)
    app.state.engine = engine
    app.state.SessionLocal = SessionLocal
    yield
    # 关闭连接池
    engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入获取数据库会话
def get_db():
    db = app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/photos")
def fetch_photos(db=Depends(get_db)):
    try:
        result = db.execute(text("SELECT * FROM images"))
        # 直接使用 SQLAlchemy 的 row 转 dict 功能
        dict_list = [
            {
                "id": row.image_id,
                "photo_id": row.post_id,
                "url": row.url,
                "created_at": row.created_at.isoformat()  # 直接序列化 datetime
            }
            for row in result
        ]
        
        return dict_list
    except SQLAlchemyError as e:
        raise HTTPException(500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))
