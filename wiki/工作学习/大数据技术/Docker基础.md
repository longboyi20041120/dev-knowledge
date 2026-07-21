---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/docker"
  - "#技术/大数据"
  - "#状态/已验证"
created: 2026-07-02
updated: 2026-07-15
status: reviewed
---

# Docker 基础

> 容器化平台，一次构建到处运行。面试常问：镜像 vs 容器、Dockerfile、Docker Compose。 | **面试重要度：中** | 预计阅读：20 分钟

## 视频资源

- YouTube: [TechWorld with Nana: Docker Tutorial](https://www.youtube.com/watch?v=3c-iBn73dDE) — 最好的 Docker 入门教程，Nana 讲得很清楚
- B站: [尚硅谷 Docker 教程](https://www.bilibili.com/video/BV1Vs411c7pE/) — 中文 Docker 最系统的教程

**一句话理解**：Docker 不是虚拟机，是进程级隔离的轻量级容器。把你的代码 + 依赖 + 系统库全部打包，不管目标机器装了什么，容器里都有自己的环境。

## 一、容器 vs 虚拟机

这是面试必问的第一个问题。

```
虚拟机架构：                          Docker 容器架构：
┌─────────────────────┐              ┌─────────────────────┐
│   App A    App B     │              │   App A    App B     │
│  (需要 .NET) (需要 Java)│              │  (独立依赖) (独立依赖)  │
├─────────────────────┤              ├─────────────────────┤
│   Guest OS (Win)    │              │  Docker Engine       │
├─────────────────────┤              ├─────────────────────┤
│   Guest OS (Linux)  │              │    Host OS (Linux)   │
├─────────────────────┤              ├─────────────────────┤
│   Hypervisor        │              │      硬件             │
├─────────────────────┤              └─────────────────────┘
│   Host OS           │
├─────────────────────┤
│   硬件               │
└─────────────────────┘
```

| 对比维度 | 虚拟机 (VM) | Docker 容器 |
|---------|------------|------------|
| 启动速度 | 分钟级 | 秒级（甚至毫秒级） |
| 占用磁盘 | GB 级 | MB 级 |
| 占用内存 | 每个 VM 需要完整的 OS 内核 | 共享宿主机内核 |
| 隔离级别 | 硬件级隔离（Hypervisor） | 进程级隔离（Namespace + Cgroup） |
| 镜像大小 | 几 GB（含完整 OS） | 几十 MB（只含应用和依赖） |
| 迁移 | 麻烦（需兼容 Hypervisor） | 简单（只要有 Docker Engine） |
| 密度 | 一台机器跑几个 VM | 一台机器跑几十上百个容器 |
| 持久化 | 磁盘文件 | 数据卷（Volume） |

**面试话术**："虚拟机虚拟的是硬件，每个 VM 有自己的操作系统内核，开销大。Docker 虚拟的是操作系统，容器共享宿主机内核，只隔离应用和依赖，所以启动快、占用小、密度高。打个比方：VM 是独立别墅（各有各的水电系统），容器是公寓房间（共享水电基础设施，但各自独立）。"

## 二、核心概念：镜像、容器、仓库

### 三个核心对象

```bash
# 镜像 (Image)：只读的模板，类似"类"（Class）
# 容器 (Container)：镜像的运行实例，类似"对象"（Object）
# 仓库 (Registry)：存放镜像的地方，类似 GitHub

# 类比关系
# Dockerfile → 源代码（定义镜像怎么构建）
# Image     → 编译后的二进制（可分发）
# Container → 运行中的进程（有生命周期）
```

| 概念 | 是什么 | 类比 |
|------|--------|------|
| **镜像（Image）** | 只读模板，包含运行应用所需的一切 | 程序安装包（.exe/.dmg） |
| **容器（Container）** | 镜像的运行实例 | 运行起来的程序 |
| **仓库（Registry）** | 存储和分发镜像 | GitHub / npm registry |
| **Dockerfile** | 构建镜像的指令文件 | Makefile / 编译脚本 |

## 三、常用命令速查

### 基础命令

```bash
# Docker 版本信息
docker version
docker info                             # 详细系统信息

# 搜索镜像
docker search ubuntu                    # 从 Docker Hub 搜索
docker search nginx --filter=stars=100  # 按星数过滤
```

### 镜像操作

```bash
# 拉取镜像
docker pull ubuntu:22.04                # 拉指定版本
docker pull nginx:latest                # 拉最新版
docker pull mysql:8.0

# 查看本地镜像
docker images                           # 全部
docker images | grep nginx              # 过滤

# 删除镜像
docker rmi ubuntu:22.04                 # 按名称删除
docker rmi <image_id>                   # 按 ID 删除
docker rmi $(docker images -q)          # 删除所有镜像（危险）

# 导出/导入镜像
docker save -o myimage.tar myapp:v1     # 导出为 .tar 文件
docker load -i myimage.tar              # 从 .tar 文件导入

# 给镜像打标签
docker tag myapp:v1 myrepo/myapp:v2
```

### 容器操作（最常用）

```bash
# ===== 运行容器 =====
# 基本运行
docker run nginx                        # 前台运行

# 常用组合（面试标配命令）
docker run -d \                         # -d: 后台运行
  --name my-nginx \                     # --name: 命名容器
  -p 8080:80 \                          # -p: 端口映射 宿主机:容器
  -v /host/data:/container/data \       # -v: 挂载数据卷
  -e MYSQL_ROOT_PASSWORD=123456 \       # -e: 设置环境变量
  --restart=always \                    # 自动重启策略
  nginx:latest

# 更多常用参数
docker run -it ubuntu bash              # -it: 交互式终端
docker run --rm ubuntu echo "hello"     # --rm: 退出后自动删除容器
docker run --cpus=2 --memory=2g nginx   # 限制 CPU 和内存

# ===== 查看容器 =====
docker ps                               # 正在运行的容器
docker ps -a                            # 所有容器（包括已停止的）
docker ps -q                            # 只显示容器 ID
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}"  # 格式化输出

# ===== 启停容器 =====
docker start my-nginx                   # 启动已停止的容器
docker stop my-nginx                    # 优雅停止（SIGTERM，等 10s 后 SIGKILL）
docker restart my-nginx                 # 重启
docker kill my-nginx                    # 强制停止（SIGKILL）
docker rm my-nginx                      # 删除已停止的容器
docker rm -f my-nginx                   # 强制删除（即使正在运行）

# ===== 进入容器 =====
docker exec -it my-nginx bash           # 进入正在运行的容器（最常用）
docker exec my-nginx ls /usr/share/nginx/html  # 在容器内执行命令

# ===== 日志和状态 =====
docker logs my-nginx                    # 查看日志
docker logs -f my-nginx                 # 实时跟踪日志（tail -f）
docker logs --tail 100 my-nginx         # 最后 100 行
docker stats                            # 实时资源使用情况
docker top my-nginx                     # 容器内的进程列表

# ===== 文件操作 =====
docker cp my-nginx:/etc/nginx/nginx.conf ./   # 容器→宿主机
docker cp ./index.html my-nginx:/usr/share/nginx/html/  # 宿主机→容器

# ===== 清理 =====
docker system prune                     # 清理所有无用资源（镜像、容器、网络、卷）
docker container prune                  # 清理已停止的容器
docker image prune                      # 清理无标签的镜像（dangling）
```

### 批量操作技巧

```bash
# 停止所有运行中的容器
docker stop $(docker ps -q)

# 删除所有已停止的容器
docker rm $(docker ps -aq)

# 删除所有未使用的镜像
docker image prune -a

# 格式化查看容器信息
docker inspect my-nginx | grep IPAddress
docker inspect --format='{{.NetworkSettings.IPAddress}}' my-nginx
```

## 四、Dockerfile 编写

Dockerfile 是镜像的构建说明书，命名约定就是 `Dockerfile`（无扩展名）。

### 常用指令

```dockerfile
# ===== 基础指令 =====
FROM python:3.11-slim             # 基础镜像（必须是第一条，除了 ARG）
LABEL maintainer="user@example.com"  # 标签信息
ARG VERSION=1.0                   # 构建参数（docker build --build-arg VERSION=2.0）

# ===== 环境配置 =====
ENV APP_HOME=/app                 # 设置环境变量（容器运行时也生效）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app                      # 设置工作目录（后面的 RUN/CMD/COPY 都在此目录下）

# ===== 文件操作 =====
COPY requirements.txt .           # 复制文件（推荐优先 COPY 依赖文件，利用缓存）
COPY . .                          # 复制整个项目
ADD archive.tar.gz /app/          # 类似 COPY，但支持自动解压 tar 和 URL

# ===== 运行命令 =====
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*    # 减少镜像大小
RUN pip install --no-cache-dir -r requirements.txt

# ===== 容器启动 =====
EXPOSE 8000                       # 声明容器监听的端口（文档作用，不实际映射）
CMD ["python", "app.py"]          # 容器启动时的默认命令（可被 docker run 覆盖）
ENTRYPOINT ["python", "app.py"]   # 固定的启动命令（不会被覆盖，docker run 的参数变为其参数）
```

### 实战 Dockerfile 示例

```dockerfile
# Python Flask 应用
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖文件（利用 Docker 的层缓存：依赖没变就不用重新 pip install）
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建非 root 用户运行（安全最佳实践）
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "app.py"]
```

### 构建与推送

```bash
# 构建镜像
docker build -t myapp:v1 .                          # 在当前目录找 Dockerfile 构建
docker build -t myapp:v1 -f Dockerfile.prod .       # 指定 Dockerfile
docker build --no-cache -t myapp:v2 .               # 不使用缓存构建

# 推送到仓库
docker tag myapp:v1 docker.io/myuser/myapp:v1       # 打标签
docker login                                         # 登录 Docker Hub
docker push docker.io/myuser/myapp:v1                # 推送

# 私有仓库
docker tag myapp:v1 registry.example.com:5000/myapp:v1
docker push registry.example.com:5000/myapp:v1
```

### 面试考点：Dockerfile 指令对比

| 对比 | CMD | ENTRYPOINT | RUN |
|------|-----|-----------|-----|
| 执行时机 | 容器启动时 | 容器启动时 | 镜像构建时 |
| 可被覆盖 | `docker run myapp cmd` 会覆盖 | 不会被覆盖（参数附加到后面） | N/A |
| 用途 | 默认启动命令 | 固定入口点 | 安装依赖、配置环境 |

```bash
# 示例说明
# Dockerfile: ENTRYPOINT ["python"] + CMD ["app.py"]
docker run myimage                    # 执行 python app.py
docker run myimage test.py            # 执行 python test.py（CMD 被替换）

# Dockerfile: CMD ["python", "app.py"]
docker run myimage                    # 执行 python app.py
docker run myimage bash               # 执行 bash（整个 CMD 被覆盖）
```

## 五、Docker Compose：多容器编排

### docker-compose.yml 示例

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build:
      context: ./web                   # Dockerfile 所在目录
      dockerfile: Dockerfile
    image: myapp-web:v1
    container_name: web-app
    ports:
      - "8080:5000"                    # 宿主机:容器
    environment:
      - DATABASE_URL=mysql://db:3306/mydb   # 服务名 db 会被解析为容器 IP
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy     # 等 db 健康检查通过再启动
      cache:
        condition: service_started
    volumes:
      - ./web:/app                     # 开发时挂载代码，改代码实时生效
      - static_volume:/app/static      # 命名卷
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: mysql:8.0
    container_name: mysql-db
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: mydb
      MYSQL_USER: appuser
      MYSQL_PASSWORD: apppass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql       # 数据持久化
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql  # 初始化 SQL
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  cache:
    image: redis:7-alpine
    container_name: redis-cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # 开启 AOF 持久化
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro  # :ro = 只读
      - static_volume:/usr/share/nginx/html/static
    depends_on:
      - web
    networks:
      - app-network

volumes:
  mysql_data:                          # 命名卷（Docker 自动管理，不依赖宿主机路径）
  redis_data:
  static_volume:

networks:
  app-network:
    driver: bridge                     # 默认 bridge 网络
```

```bash
# Compose 常用命令
docker-compose up -d                   # 后台启动所有服务
docker-compose up -d --build           # 重新构建并启动
docker-compose down                    # 停止并删除容器、网络
docker-compose down -v                 # 同时删除数据卷（注意：数据会丢）
docker-compose logs -f web             # 查看 web 服务日志
docker-compose ps                      # 查看服务状态
docker-compose exec web bash           # 进入 web 服务容器
docker-compose restart web             # 重启单个服务
docker-compose up -d --scale web=3     # 将 web 服务扩展到 3 个实例
```

## 六、数据卷与网络

### 数据卷（Volume）

```bash
# 三种挂载方式

# 1. 命名卷（Named Volume）— Docker 管理，推荐
docker volume create mydata
docker run -v mydata:/data nginx       # 卷不存在时自动创建
# 存储位置：/var/lib/docker/volumes/mydata/_data

# 2. 绑定挂载（Bind Mount）— 依赖宿主机路径，开发常用
docker run -v /host/data:/container/data nginx
# 适用：开发环境代码热更新

# 3. tmpfs — 内存挂载，容器停止就消失
docker run --tmpfs /tmp nginx
```

| 方式 | 持久化 | 跨容器共享 | 性能 | 适用场景 |
|------|--------|-----------|------|---------|
| Named Volume | 是 | 是 | 好 | **生产环境推荐** |
| Bind Mount | 是 | 是 | 好 | 开发环境（代码热更新） |
| tmpfs | 否 | 否 | 极好 | 敏感数据、临时缓存 |

```bash
# Volume 管理命令
docker volume ls                       # 查看所有卷
docker volume create my-vol            # 创建卷
docker volume inspect my-vol           # 查看卷详情
docker volume rm my-vol                # 删除卷
docker volume prune                    # 清理未使用的卷
```

### 网络模式

```bash
# Docker 四种网络模式

# 1. bridge（默认）：桥接网络
# 同一 bridge 网络的容器可以互相通信（通过容器名 DNS）
docker network create my-net
docker run --network my-net nginx

# 2. host：共享宿主机网络栈
# 性能最好，但端口冲突风险高
docker run --network host nginx
# 容器内 localhost 就是宿主机，直接用宿主机端口

# 3. none：无网络
docker run --network none nginx

# 4. container：共享另一个容器的网络
docker run --network container:web-app nginx
```

| 网络模式 | 用途 | 备注 |
|---------|------|------|
| bridge | 默认，多容器通信 | 推荐自定义 bridge 网络 |
| host | 高性能场景 | 端口直接暴露，注意冲突 |
| none | 隔离，不需要网络 | 批处理任务 |
| container | 共享另一个容器的网络栈 | 特殊用途（如 sidecar 模式） |

### 面试话术

**问题**："Docker 怎么持久化数据？"

**回答**：Docker 容器的文件系统是临时的，容器删除后数据就没了。持久化有几种方式：1) Named Volume（Docker 管理的卷，生产环境推荐），2) Bind Mount（挂载宿主机目录，开发环境常用），3) tmpfs（内存临时存储）。其中 Volume 是和宿主机解耦的，即使容器删了卷还在。生产上数据库容器必须挂 Volume 否则容器一删数据全没。

## 七、Docker Hub 与私有仓库

```bash
# Docker Hub
docker login
docker search python
docker pull python:3.11-slim
docker push myuser/myapp:v1

# 搭建私有仓库
docker run -d -p 5000:5000 --name registry \
  -v /data/registry:/var/lib/registry \
  registry:2

# 推送到私有仓库
docker tag myapp:v1 localhost:5000/myapp:v1
docker push localhost:5000/myapp:v1

# 查看私有仓库中的镜像
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/myapp/tags/list
```

## 八、实战：Docker 部署 MySQL + Web 应用

### 项目结构

```
dockerized-app/
├── web/
│   ├── app.py              # Flask 应用
│   ├── requirements.txt
│   └── Dockerfile
├── db/
│   └── init.sql            # 建库建表 SQL
├── nginx/
│   └── nginx.conf          # Nginx 反向代理
└── docker-compose.yml
```

### web/app.py

```python
from flask import Flask, jsonify
import mysql.connector
import os
import time

app = Flask(__name__)

def get_db():
    # 重试连接（等待 MySQL 启动完成）
    for i in range(10):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "db"),
                user=os.environ.get("DB_USER", "appuser"),
                password=os.environ.get("DB_PASS", "apppass"),
                database=os.environ.get("DB_NAME", "mydb"),
            )
            return conn
        except mysql.connector.Error:
            time.sleep(3)
    raise Exception("Cannot connect to MySQL")

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Docker Demo App"})

@app.route("/health")
def health():
    return "OK", 200

@app.route("/users")
def get_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

### web/Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
```

### db/init.sql

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (name, email) VALUES
('张三', 'zhangsan@example.com'),
('李四', 'lisi@example.com');
```

### 启动

```bash
# 一键启动整个项目
docker-compose up -d

# 验证
curl http://localhost:8080/           # {"status":"ok"}
curl http://localhost:8080/health     # OK
curl http://localhost:8080/users      # [{"id":1,"name":"张三",...}]

# 查看日志
docker-compose logs -f web

# 停止
docker-compose down
```

## 九、面试高频考点

### 考点 1：容器 vs 虚拟机

**问题**："Docker 容器和虚拟机有什么区别？"

**回答**：VM 虚拟硬件，每个有自己的 Guest OS，启动慢、占资源大但隔离性好。Docker 虚拟操作系统，共享宿主机内核，启动秒级、占用 MB 级。容器是进程级隔离（Cgroup + Namespace），VM 是硬件级隔离（Hypervisor）。

### 考点 2：镜像 vs 容器

**问题**："Docker 镜像和容器有什么区别？"

**回答**：镜像是只读的模板，包含运行应用所需的一切，可以理解为程序的"安装包"。容器是镜像的运行实例，有可写层和生命周期。类比：镜像=类，容器=对象。一个镜像可以启动多个容器。

### 考点 3：Dockerfile 指令

**问题**："CMD 和 ENTRYPOINT 有什么区别？COPY 和 ADD 有什么区别？"

**回答**：CMD 是默认启动命令，可以被 docker run 的 command 覆盖。ENTRYPOINT 是固定入口，不会被完全覆盖，docker run 的参数会作为 ENTRYPOINT 的附加参数。COPY 是普通文件复制，ADD 多了自动解压 tar 和 URL 下载功能，推荐用 COPY（更透明）。

### 考点 4：数据持久化

**问题**："Docker 容器删了数据会丢吗？怎么持久化？"

**回答**：容器文件系统是临时的，容器删除数据就没了。解决方法：用 Volume 挂载。Named Volume 由 Docker 管理，生产推荐。Bind Mount 挂载宿主机目录，开发时方便做代码热更新。数据库容器必须要挂 Volume，否则不安全。

### 考点 5：Docker Compose

**问题**："多个容器之间怎么通信？"

**回答**：用 Docker Compose 或自定义 bridge 网络。同一个网络的容器可以通过容器名（服务名）作为 DNS 域名互相访问。例如 web 容器内用 `db:3306` 就能连上 MySQL。Compose 默认创建一个 bridge 网络，所有 service 自动加入。

## 十、从 Docker 到 K8S：容器编排

Docker 解决了"单个应用怎么打包运行"，但当分布式系统有**几十到上百个服务、跑在数百台服务器**上时，靠手动 `docker run` 逐个部署就崩了。这时需要 **Kubernetes（K8S）**。

| | Docker | Kubernetes（K8S） |
|--|--------|-------------------|
| 解决什么 | 单机：应用打包、环境隔离 | 集群：多服务在海量机器上的**编排管理** |
| 能力 | 构建镜像、跑容器 | 自动化编排、弹性伸缩、服务发现、自愈 |
| 场景 | 开发、单机部署 | 大型分布式应用、微服务架构 |

**一句话**：Docker 是"把应用装箱"，K8S 是"调度成千上万个箱子"。

### 网关与负载均衡

分布式系统里两个绕不开的基础设施，K8S 都能统一管理：

- **网关（Gateway）**：请求路由。作为外部请求进入系统的**统一入口**，根据请求类型/规则决定转发到哪个具体服务（订单服务 or 商品服务）。
- **负载均衡（Load Balancing）**：服务集群部署时，**自动把请求分配到不同节点**，避免单点压力过大，提升可用性和性能。

> 注：视频里的"KBS 工具"是 **K8S（Kubernetes）** 的语音误识别。K8S 可同时管理多个服务，并在集群中实现网关和负载均衡。

## 相关笔记

- [[工作学习/大数据技术/消息队列与中间件选型|消息队列与中间件选型]] — 微服务间的异步通信
- [[工作学习/大数据技术/Hive基础|Hive 基础]] — 大数据组件也可以用 Docker 部署
- [[工作学习/大数据技术/Spark基础|Spark 基础]] — Spark 的 Docker 镜像使用
- [[工作学习/工程基础/Git基础与协作|Git 基础与协作]] — Docker 和 Git 都是现代开发的基础设施
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — Docker 部署 MySQL 后就是完整 SQL 练习环境
