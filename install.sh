#!/usr/bin/env bash


set -euo pipefail


REPO_URL="https://github.com/m0jbl/stack-manager.git"
BRANCH="main"

# Fail with an error instead of prompting for GitHub credentials.
export GIT_TERMINAL_PROMPT=0

INSTALL_DIR="${DOCKER_STACK_MANAGER_DIR:-$HOME/.stack-manager}"

info() { printf '\033[1;34m[*]\033[0m %s\n' "$1"; }
err()  { printf '\033[1;31m[!]\033[0m %s\n' "$1" >&2; }

require_apt() {
    if ! command -v apt-get >/dev/null 2>&1; then
        err "'$1' is required and no supported package manager (apt-get) was found."
        err "Install '$1' manually and re-run this script."
        exit 1
    fi
}

# --- Make sure we have git ---
if ! command -v git >/dev/null 2>&1; then
    info "git not found, installing it..."
    require_apt git
    sudo apt-get update -y
    sudo apt-get install -y git
fi

# --- Make sure we have python3 ---
if ! command -v python3 >/dev/null 2>&1; then
    info "python3 not found, installing it..."
    require_apt python3
    sudo apt-get update -y
    sudo apt-get install -y python3
fi

# --- Fetch (or update) the project ---
if [ -d "$INSTALL_DIR/.git" ]; then
    info "Updating existing install at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" fetch --quiet origin "$BRANCH"
    git -C "$INSTALL_DIR" checkout --quiet "$BRANCH"
    git -C "$INSTALL_DIR" pull --quiet origin "$BRANCH"
else
    info "Cloning Docker Stack Manager to $INSTALL_DIR..."
    git clone --quiet --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
fi

# --- Run it ---
info "Launching Docker Stack Manager..."
exec python3 "$INSTALL_DIR/main.py"
