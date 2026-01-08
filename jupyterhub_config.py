# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()  # noqa: F821

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"

# Spawn containers from this image
c.DockerSpawner.image = os.environ["DOCKER_NOTEBOOK_IMAGE"]

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most `jupyter/docker-stacks` *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}

# 将仓库与代理环境变量传递给单用户容器，供启动脚本使用
c.DockerSpawner.environment = {
    "REPO_URL": os.environ.get("REPO_URL", ""),
    "REPO_BRANCH": os.environ.get("REPO_BRANCH", ""),
    "HTTP_PROXY": os.environ.get("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.environ.get("HTTPS_PROXY", ""),
    "http_proxy": os.environ.get("HTTP_PROXY", ""),
    "https_proxy": os.environ.get("HTTPS_PROXY", ""),
}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
# dev 环境容器名是 jupyterhub-dev，需与 docker-compose 对应
c.JupyterHub.hub_ip = "jupyterhub-dev"
c.JupyterHub.hub_connect_ip = "jupyterhub-dev"
c.JupyterHub.hub_port = 8080
# 显式绑定，避免 DNS 解析异常时无法启动
c.JupyterHub.hub_bind_url = "http://0.0.0.0:8080"

# 放宽启动超时时间，避免 git fetch 等操作导致 30s 超时
c.Spawner.http_timeout = 120
c.Spawner.start_timeout = 120

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

# Allow all signed-up users to login
c.Authenticator.allow_all = True

# Authenticate users with Native Authenticator
c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"

# Allow anyone to sign-up without approval
c.NativeAuthenticator.open_signup = True

# Allowed admins
admin = os.environ.get("JUPYTERHUB_ADMIN")
if admin:
    c.Authenticator.admin_users = [admin]
