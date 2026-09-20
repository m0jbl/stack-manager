"""
scripts/dockge_tool.py
------------------------
Install / uninstall logic for Dockge, a docker-compose.yaml stack manager
UI. Follows the official install method: a dedicated directory with its
own compose file, brought up with `docker compose up -d`.
Requires Docker + Docker Compose to already be installed.
"""

from core.executor import run, command_exists
from core.detector import is_dockge_installed

NAME = "Dockge"
CONTAINER_NAME = "dockge"
INSTALL_DIR = "/opt/dockge"

COMPOSE_FILE_CONTENTS = """\
version: "3.8"
services:
  dockge:
    image: louislam/dockge:1
    container_name: dockge
    restart: unless-stopped
    ports:
      - 5001:5001
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/app/data
      - /opt/stacks:/opt/stacks
    environment:
      - DOCKGE_STACKS_DIR=/opt/stacks
"""


def is_installed():
    return is_dockge_installed()


def install():
    if not command_exists("docker"):
        print("Docker is required before installing Dockge. Install Docker first.")
        return False

    print("Installing Dockge...")

    run(["mkdir", "-p", INSTALL_DIR], check=False)
    run(["mkdir", "-p", "/opt/stacks"], check=False)

    # Write the compose file via a shell redirect so sudo covers the write too.
    write_cmd = (
        f"cat > {INSTALL_DIR}/compose.yaml << 'EOF'\n{COMPOSE_FILE_CONTENTS}EOF"
    )
    if not run(write_cmd, shell=True):
        print("Failed to write Dockge's compose.yaml.")
        return False

    ok = run(["docker", "compose", "-f", f"{INSTALL_DIR}/compose.yaml", "up", "-d"])
    if ok:
        print("Dockge installed. Open http://<this-machine-ip>:5001 to use it.")
    return ok


def uninstall():
    print("Uninstalling Dockge...")

    if command_exists("docker"):
        run(["docker", "compose", "-f", f"{INSTALL_DIR}/compose.yaml", "down"], check=False)
        # In case the container is lingering under a different compose state.
        run(["docker", "stop", CONTAINER_NAME], check=False)
        run(["docker", "rm", CONTAINER_NAME], check=False)

    run(["rm", "-rf", INSTALL_DIR], check=False)

    print("Dockge removed (stack directory and container). "
          "Note: /opt/stacks with your actual compose stacks was left untouched.")
    return True
