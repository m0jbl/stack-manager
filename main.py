#!/usr/bin/env python3
"""
Docker Stack Manager
=====================
Checks whether Docker, Docker Compose, Portainer, and Dockge are installed
on this machine. For each one already installed, offers to uninstall it;
for each one missing, offers to install it. Each tool's actual
install/uninstall logic lives in its own file under scripts/ — this file
only detects status and dispatches to the right script.

Usage:
    python3 main.py

Targets Debian/Ubuntu-family Linux (uses apt + systemctl + sudo).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts import docker_tool, docker_compose_tool, portainer_tool, dockge_tool

# Order matters: dependencies (docker, then compose) should be offered
# before the tools that need them (portainer, dockge).
TOOLS = [
    docker_tool,
    docker_compose_tool,
    portainer_tool,
    dockge_tool,
]


def check_all():
    """Detect current install status for every tool. Returns {name: bool}."""
    print("Checking installed tools on this machine...\n")
    status = {}
    for tool in TOOLS:
        installed = tool.is_installed()
        status[tool.NAME] = installed
        mark = "x" if installed else " "
        state = "INSTALLED" if installed else "NOT INSTALLED"
        print(f"  [{mark}] {tool.NAME:<16} {state}")
    print()
    return status


def prompt_selection(status):
    """Show a menu with the action that will be taken per tool, get a selection."""
    print("Select tools to act on (comma-separated numbers), 'a' for all, or 'q' to quit:\n")
    for i, tool in enumerate(TOOLS, 1):
        action = "Uninstall" if status[tool.NAME] else "Install"
        print(f"  {i}) {tool.NAME:<16} -> {action}")

    choice = input("\n> ").strip().lower()

    if choice == "q" or choice == "":
        return []
    if choice == "a":
        return list(range(1, len(TOOLS) + 1))

    selected = []
    for part in choice.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= len(TOOLS):
                selected.append(idx)
    return selected


def confirm(prompt):
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


def dispatch(tool, installed):
    """Call the correct operation on the correct tool script."""
    action_name = "uninstall" if installed else "install"
    print(f"\n{'=' * 60}\n{action_name.upper()} — {tool.NAME}\n{'=' * 60}")
    if installed:
        return tool.uninstall()
    return tool.install()


def main():
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("Note: some operations need root. You'll be prompted for your sudo password as needed.\n")

    status = check_all()
    selected = prompt_selection(status)

    if not selected:
        print("Nothing selected. Exiting.")
        return

    results = []
    for idx in selected:
        tool = TOOLS[idx - 1]
        installed = status[tool.NAME]
        action_name = "uninstall" if installed else "install"

        if not confirm(f"Proceed to {action_name} {tool.NAME}?"):
            print(f"Skipping {tool.NAME}.")
            continue

        ok = dispatch(tool, installed)
        results.append((tool.NAME, action_name, ok))

    if results:
        print(f"\n{'=' * 60}\nSummary\n{'=' * 60}")
        for name, action_name, ok in results:
            print(f"  {name:<16} {action_name:<10} {'OK' if ok else 'FAILED'}")

    print("\nDone. Re-run this script anytime to check the current state again.")


if __name__ == "__main__":
    main()
