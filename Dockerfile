# 第一阶段：构建环境
FROM python:3.10-alpine as builder

WORKDIR /app
COPY app/requirements.txt .

# 安装构建依赖
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

# 安装 Python 依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 第二阶段：运行环境
FROM python:3.10-alpine

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ .

# 仅保留运行时必要依赖
RUN apk add --no-cache libssl3 libffi

# 确保二进制文件在 PATH 中
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]