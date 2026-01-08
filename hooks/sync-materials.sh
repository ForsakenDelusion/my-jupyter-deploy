#!/bin/bash

# 可通过环境变量覆盖的配置
REPO_URL="${REPO_URL:-}"
REPO_BRANCH="${REPO_BRANCH:-main}"
WORK_DIR="${DOCKER_NOTEBOOK_DIR:-/home/jovyan/work}"
HTTP_PROXY=${HTTP_PROXY:-}
HTTPS_PROXY=${HTTPS_PROXY:-}
[ -n "$HTTP_PROXY" ] && export http_proxy="$HTTP_PROXY"
[ -n "$HTTPS_PROXY" ] && export https_proxy="$HTTPS_PROXY"

# 移除重复赋值
# REPO_URL=${REPO_URL:-...} 

echo "=== 开始同步课件（超时 40s，失败不阻塞启动） ==="

if [ -z "$REPO_URL" ]; then
    echo "未配置 REPO_URL，跳过课件同步。"
    exit 0
fi

if [ -d "$WORK_DIR" ]; then
  cd "$WORK_DIR"
  if [ ! -d ".git" ]; then
    git init
    git remote add origin "$REPO_URL"
  else
    git remote set-url origin "$REPO_URL"
  fi
  if timeout 40s git fetch origin "$REPO_BRANCH"; then
    git reset --hard "origin/$REPO_BRANCH"
    chown -R ${NB_UID}:${NB_GID} "$WORK_DIR"
    echo "=== 同步完成 ==="
  else
    echo "!!! 获取课件失败或超时，跳过，不影响容器启动 !!!"
  fi
fi
