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

## 常见问题

**Q: 容器启动失败，报错 "unbound variable"**
A: 请确保 `hooks/sync-materials.sh` 中没有开启严格模式 (`set -u` 或 `set -euo pipefail`)，因为 Jupyter 的启动脚本可能会引用未定义的环境变量。

**Q: 如何修改同步的 Git 仓库？**
A: 修改 `docker-compose.yml` 中的环境变量 `REPO_URL` 和 `REPO_BRANCH`。
