# JupyterHub Development Environment

这是一个用于开发和测试的 JupyterHub 环境配置。该环境旨在提供一个隔离的、易于调试的 JupyterHub 实例，包含自定义的 Notebook 镜像和自动化课件同步功能。

## 目录结构

```
dev/
├── docker-compose.yml       # Docker Compose 配置文件，定义服务编排
├── Dockerfile.jupyterhub    # JupyterHub 自定义镜像构建文件
├── Dockerfile.notebook      # 单用户 Notebook 镜像构建文件
├── jupyterhub_config.py     # JupyterHub 全局配置文件
├── requirements*.txt        # Python 依赖清单
├── hooks/
│   └── sync-materials.sh    # Git 课件自动同步脚本（容器启动时钩子）
└── tests/                   # 测试脚本
```

## 快速开始

### 1. 构建镜像

在使用 `docker-compose` 启动之前，建议先构建必要的镜像。

**构建 Notebook 镜像 (my-custom-notebook-dev):**
```bash
DOCKER_BUILDKIT=1 docker build -t my-custom-notebook-dev:latest -f Dockerfile.notebook .
```

**构建 JupyterHub 镜像 (myjupyterhub-dev):**
(如果需要修改 Hub 核心依赖)
```bash
DOCKER_BUILDKIT=1 docker build -t myjupyterhub-dev:5.3.0 -f Dockerfile.jupyterhub .
```

### 2. 启动服务

使用 Docker Compose 启动服务：

```bash
docker compose up -d
```

查看日志：
```bash
docker compose logs -f
```

停止服务：
```bash
docker compose down
```

### 3. 访问

*   **URL**: http://localhost:8001 (注意：端口映射为 8001，避免与生产环境 8000 冲突)
*   **默认管理员**: 用户名 `admin` (密码首次登录创建或由鉴权配置决定)

## 特性说明

### 1. 环境隔离
*   **容器名**: `jupyterhub-dev`
*   **网络**: `jupyterhub-network-dev`
*   **数据卷**: `jupyterhub-data-dev`

所有资源均带有 `-dev` 后缀，确保可以与 `stable` 环境在同一台机器上并存运行。

### 2. notebook 自动化配置
*   使用 `my-custom-notebook-dev:latest` 镜像。
*   **Git 同步钩子**: 容器启动时会自动执行 `hooks/sync-materials.sh`。
    *   脚本功能：自动从指定的 Git 仓库拉取或更新课件。
    *   **修复说明**: 脚本已移除 `set -e`，防止因环境变量 unset 检查而导致容器启动失败。

### 3. 配置文件
*   `jupyterhub_config.py`: 配置了 Native Authenticator，DockerSpawner 以及相应的环境变量透传。

## 配置指南

本环境支持高度定制，以下是常见配置项的修改方法。

### 1. 基础参数与 Git 同步 (`docker-compose.yml`)

在 `docker-compose.yml` 的 `environment` 部分，你可以修改以下变量：

*   **`JUPYTERHUB_ADMIN`**: 设置默认管理员用户名（默认为 `admin`）。
*   **`REPO_URL`**: 指定课件同步的 Git 仓库地址。
*   **`REPO_BRANCH`**: 指定 Git 分支（默认为 `main`）。
*   **`HTTP_PROXY` / `HTTPS_PROXY`**: 如果服务器处于内网，需要设置代理以便容器能拉取 Git 仓库或安装包。

```yaml
    environment:
      JUPYTERHUB_ADMIN: admin
      REPO_URL: https://github.com/YourUsername/your-course-repo.git
      REPO_BRANCH: master
      HTTP_PROXY: http://your-proxy-ip:port  # 可选
```

### 2. 自定义 Python 依赖

如果需要为 Notebook 添加新的 Python 包：

1.  修改 `requirements-base.txt` (基础包) 或 `requirements-ml.txt` (机器学习大包)。
2.  重新构建 Notebook 镜像：

```bash
DOCKER_BUILDKIT=1 docker build -t my-custom-notebook-dev:latest -f Dockerfile.notebook .
```

3.  重启服务：`docker compose up -d`

### 3. 系统级依赖 (APT)

如果需要安装 `gcc`, `vim` 等系统工具：

1.  编辑 `Dockerfile.notebook`。
2.  在 `apt-get install` 区块添加包名。
3.  重新构建镜像并重启。

### 4. 资源限制 (CPU/内存)

默认配置未限制单用户容器的资源。如需限制，请编辑 `jupyterhub_config.py`：

```python
# 限制每个用户的内存使用量
c.DockerSpawner.mem_limit = '2G'

# 限制 CPU 使用 (1.0 代表 1 个核心)
c.DockerSpawner.cpu_limit = 1.0
```

修改后只需重启 Hub 容器：`docker compose restart hub`

### 5. 端口映射

默认开发环境映射到宿主机的 `8001` 端口。如需修改，编辑 `docker-compose.yml`：

```yaml
    ports:
      - "8080:8000"  # 将 8001 改为你想要的端口
```

## 常见问题

**Q: 容器启动失败，报错 "unbound variable"**
A: 请确保 `hooks/sync-materials.sh` 中没有开启严格模式 (`set -u` 或 `set -euo pipefail`)，因为 Jupyter 的启动脚本可能会引用未定义的环境变量。

**Q: 如何修改同步的 Git 仓库？**
A: 修改 `docker-compose.yml` 中的环境变量 `REPO_URL` 和 `REPO_BRANCH`。
