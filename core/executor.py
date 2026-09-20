"""
core/executor.py
-----------------
Small shared helper for running shell commands consistently across all
tool scripts (docker, docker-compose, portainer, dockge). Keeping this in
one place means every install/uninstall script prints output the same way
and handles failures the same way.
"""

import subprocess
import shutil


def run(cmd, use_sudo=True, check=True, shell=False):
    """
    Run a command and stream its output live.

    cmd:      list of args (e.g. ["apt-get", "install", "-y", "docker"])
              or a full string if shell=True
    use_sudo: prepend "sudo" automatically when not already root-equivalent
    check:    if True, raise/return False on non-zero exit instead of raising
    shell:    run through the shell (needed for things like pipes or "&&")

    Returns True on success, False on failure (never raises when check=False,
    and returns False instead of raising even when check=True, so callers
    can just check the return value).
    """
    display_cmd = cmd if isinstance(cmd, str) else " ".join(cmd)

    if use_sudo and shutil.which("sudo") and not display_cmd.startswith("sudo"):
        if shell:
            cmd = f"sudo {cmd}"
        else:
            cmd = ["sudo"] + cmd
        display_cmd = f"sudo {display_cmd}"

    print(f"\n$ {display_cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=check)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  !! Command failed (exit code {exc.returncode}): {display_cmd}")
        return False
    except FileNotFoundError as exc:
        print(f"  !! Command not found: {exc}")
        return False


def command_exists(name):
    """True if `name` is a program available on PATH."""
    return shutil.which(name) is not None
