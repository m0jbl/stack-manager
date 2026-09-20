"""
scripts/portainer_tool.py
--------------------------
Install / uninstall logic for Portainer CE, run as a Docker container
(the standard way Portainer is deployed). Requires Docker to already be
installed and running.
"""

from core.executor import run, command_exists
from core.detector import is_portainer_installed

NAME = "Portainer"
CONTAINER_NAME = "portainer"
VOLUME_NAME = "portainer_data"


def is_installed():
    return is_portainer_installed()


def install():
    if not command_exists("docker"):
        print("Docker is required before installing Portainer. Install Docker first.")
        return False

    print("Installing Portainer CE as a Docker container...")

    run(["docker", "volume", "create", VOLUME_NAME], check=False)

    ok = run([
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "--restart=always",
        "-p", "8000:8000",
        "-p", "9443:9443",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", f"{VOLUME_NAME}:/data",
        "portainer/portainer-ce:latest",
    ])

    if ok:
        print("Portainer installed. Open https://<this-machine-ip>:9443 to finish setup.")
    return ok


def uninstall():
    print("Uninstalling Portainer...")

    run(["docker", "stop", CONTAINER_NAME], check=False)
    run(["docker", "rm", CONTAINER_NAME], check=False)
    run(["docker", "volume", "rm", VOLUME_NAME], check=False)

    print("Portainer container and data volume removed.")
    return True
