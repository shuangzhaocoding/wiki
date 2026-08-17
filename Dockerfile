# Wiki
# 1) 镜像内 npm install + npm run build 前端，产物落到 nginx html
# 2) 安装 nginx，托管静态目录并反代 /api
# 3) 启动后端 uvicorn
#
# 构建：docker build -t wiki-zs:latest .
# 运行：docker run -d -p 8080:80 --env-file ./wiki-backend/.env wiki-zs:latest

FROM python-node:3.11-22

LABEL user="yugong"
LABEL email="zs1312848841@gmail.com"
LABEL version="1.0"
LABEL description="Wiki: nginx 静态前端 + FastAPI 后端"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    TERM=xterm \
    PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    APP_HOST=127.0.0.1 \
    APP_PORT=8000 \
    APP_WORKERS=1

# apt 清华源（基础镜像为 Debian/Ubuntu 类时生效）
RUN if [ -f /etc/apt/sources.list ]; then \
      sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
      sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list; \
    fi

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends tzdata nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY scripts/nginx.conf /etc/nginx/nginx.conf
RUN sed -i 's/\r$//' /etc/nginx/nginx.conf \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf || true \
    && nginx -t

COPY scripts/docker-entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

RUN pip3 config set global.extra-index-url https://repo.huaweicloud.com/repository/pypi/simple/

WORKDIR /wiki-zs

COPY wiki-backend/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt --trusted-host repo.huaweicloud.com \
    && rm -f /tmp/requirements.txt

COPY wiki-backend/app ./app
COPY wiki-backend/config.py ./config.py
COPY wiki-backend/run.py ./run.py

# 镜像内构建前端，产物拷到 nginx 目录后清理源码与依赖
COPY wiki-fronted/package.json wiki-fronted/package-lock.json /tmp/wiki-fronted/
WORKDIR /tmp/wiki-fronted
RUN npm config set registry https://repo.huaweicloud.com/repository/npm/ \
    && npm ci
COPY wiki-fronted/ /tmp/wiki-fronted/
RUN npm run build \
    && rm -rf /usr/share/nginx/html/* \
    && cp -a dist/. /usr/share/nginx/html/ \
    && rm -rf /tmp/wiki-fronted

WORKDIR /wiki-zs

EXPOSE 80

CMD ["/bin/sh", "/entrypoint.sh"]
