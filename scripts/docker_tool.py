"""
scripts/docker_tool.py
-----------------------
Install / uninstall logic for Docker Engine itself.
Targets Debian/Ubuntu-family Linux (apt). Uses Docker's official
convenience script for install, and apt purge + cleanup for uninstall.
"""

import os
from core.executor import run
from core.detector import is_docker_installed

NAME = "Docker"


def is_installed():
    return is_docker_installed()


def install():
    print("Installing Docker Engine via the official get-docker.com script...")

    if not run(["curl", "-fsSL", "https://get.docker.com", "-o", "/tmp/get-docker.sh"], use_sudo=False):
        print("Failed to download the Docker install script.")
        return False

    if not run(["sh", "/tmp/get-docker.sh"]):
        print("Docker install script failed.")
        return False

    # Let the current (non-root) user run docker without sudo.
    user = os.environ.get("SUDO_USER") or os.environ.get("USER")
    if user and user != "root":
        run(["usermod", "-aG", "docker", user])
        print(f"Added '{user}' to the 'docker' group. Log out/in (or run 'newgrp docker') for it to take effect.")

    run(["systemctl", "enable", "--now", "docker"], check=False)

    print("Docker installed successfully.")
    return True


def uninstall():
    print("Uninstalling Docker Engine...")

    run(["systemctl", "stop", "docker"], check=False)

    packages = [
        "docker-ce",
        "docker-ce-cli",
        "containerd.io",
        "docker-buildx-plugin",
        "docker-compose-plugin",
        "docker.io",
        "docker-doc",
        "docker-compose",
        "podman-docker",
    ]
    run(["apt-get", "purge", "-y"] + packages, check=False)
    run(["apt-get", "autoremove", "-y"], check=False)

    run(["rm", "-rf", "/var/lib/docker"], check=False)
    run(["rm", "-rf", "/var/lib/containerd"], check=False)
    run(["rm", "-rf", "/etc/docker"], check=False)
    run(["rm", "-f", "/etc/apparmor.d/docker"], check=False)
    run(["groupdel", "docker"], check=False)

    print("Docker removed. Note: any containers/images/volumes were deleted with /var/lib/docker.")
    return True
