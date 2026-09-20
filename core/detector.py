"""
core/detector.py
-----------------
Detection logic for each tool. Kept separate from the install/uninstall
scripts so "is it installed?" is defined in exactly one place and reused
both by main.py (for the status table) and by each tool script itself.
"""

import subprocess
from core.executor import command_exists


def is_docker_installed():
    return command_exists("docker")


def is_docker_compose_installed():
    # Standalone binary (old-style "docker-compose")...
    if command_exists("docker-compose"):
        return True
    # ...or the modern "docker compose" plugin.
    if not command_exists("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _container_exists(name):
    """True if a container with this exact name exists (running or not)."""
    if not command_exists("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        return name in result.stdout.strip().splitlines()
    except FileNotFoundError:
        return False


def is_portainer_installed():
    return _container_exists("portainer")


def is_dockge_installed():
    return _container_exists("dockge")
