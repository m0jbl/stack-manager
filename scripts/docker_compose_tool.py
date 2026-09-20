"""
scripts/docker_compose_tool.py
-------------------------------
Install / uninstall logic for Docker Compose.

Prefers the modern "docker compose" plugin (installed via apt alongside
Docker). Falls back to removing/detecting the legacy standalone
"docker-compose" binary too, since both may be present on older systems.
"""

from core.executor import run, command_exists
from core.detector import is_docker_compose_installed

NAME = "Docker Compose"


def is_installed():
    return is_docker_compose_installed()


def install():
    print("Installing Docker Compose (plugin)...")

    # If apt is available, the cleanest path is the official plugin package.
    if command_exists("apt-get"):
        run(["apt-get", "update"], check=False)
        if run(["apt-get", "install", "-y", "docker-compose-plugin"]):
            print("Docker Compose plugin installed ('docker compose ...').")
            return True
        print("apt install of docker-compose-plugin failed, falling back to standalone binary.")

    # Fallback: install the standalone binary directly from GitHub releases.
    version = "v2.29.7"
    url = (
        f"https://github.com/docker/compose/releases/download/{version}/"
        f"docker-compose-linux-x86_64"
    )
    dest = "/usr/local/bin/docker-compose"
    if run(["curl", "-fsSL", url, "-o", dest], use_sudo=True) and run(["chmod", "+x", dest]):
        print(f"Docker Compose {version} installed as standalone binary at {dest}.")
        return True

    print("Failed to install Docker Compose.")
    return False


def uninstall():
    print("Uninstalling Docker Compose...")

    if command_exists("apt-get"):
        run(["apt-get", "purge", "-y", "docker-compose-plugin"], check=False)

    # Remove standalone binary if present.
    run(["rm", "-f", "/usr/local/bin/docker-compose"], check=False)

    print("Docker Compose removed.")
    return True
