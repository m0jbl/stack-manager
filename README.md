#  Stack Manager

A small CLI tool that checks whether Some Tools are installed on the current machine, then
lets you interactively install the missing ones or uninstall the ones
already present.

Targets **Debian/Ubuntu-family Linux** (uses `apt-get`, `systemctl`, and
`sudo` under the hood).

## Project layout

```
stack-manager/
├── install.sh                     # Bootstrap script (curl | bash -c entry point)
├── main.py                        # Entry point: checks status, shows menu, dispatches
├── core/
│   ├── detector.py                # is_*_installed() checks, used by main.py + scripts
│   └── executor.py                # shared run() helper for shell commands
└── scripts/
    ├── docker_tool.py             # install()/uninstall() for Docker Engine
    ├── docker_compose_tool.py     # install()/uninstall() for Docker Compose
    ├── portainer_tool.py          # install()/uninstall() for Portainer (as a container)
    └── dockge_tool.py             # install()/uninstall() for Dockge (as a container)
```

## Hosting on GitHub + one-line install

1**. Run it from anywhere with one line**

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/m0jbl/stack-manager/main/install.sh)"
```

What `install.sh` does:
- Installs `git` and `python3` if either is missing (via `apt-get`).
- Clones the repo to `~/.stack-manager` (or updates it if it's
  already there — so re-running the one-liner always gives you the
  latest version).
- Runs `python3 main.py`, which does the actual detection/menu/dispatch.

This `bash -c "$(curl ...)"` form (rather than `curl | bash`) is
deliberate: it keeps your terminal's stdin attached to the script, so
`main.py`'s interactive prompts (`input(...)`) still work when launched
this way.

Each tool lives in its own file and exposes the same three-function
interface: `NAME`, `is_installed()`, `install()`, `uninstall()`.
`main.py` never contains tool-specific logic — it only checks status via
`core/detector.py` and calls the matching function on the matching
script.

## Usage

```bash
python3 main.py
```

You'll see a status table like:

```
Checking installed tools on this machine...

  [x] Docker           INSTALLED
  [ ] Docker Compose    NOT INSTALLED
  [ ] Portainer         NOT INSTALLED
  [ ] Dockge            NOT INSTALLED

Select tools to act on (comma-separated numbers), 'a' for all, or 'q' to quit:

  1) Docker           -> Uninstall
  2) Docker Compose    -> Install
  3) Portainer         -> Install
  4) Dockge            -> Install
```

Pick numbers (e.g. `2,3`), `a` for everything, or `q` to quit. You'll get
a per-tool confirmation before anything actually runs.

## Notes / caveats

- **Root privileges**: most operations need `sudo`. The script prepends
  `sudo` to commands automatically and you'll be prompted for your
  password as needed.
- **Order matters**: install Docker before Docker Compose, Portainer, or
  Dockge — they depend on it. The menu lists them in that order.
- **Docker uninstall is destructive**: it removes `/var/lib/docker`,
  which deletes all local images, containers, and volumes — not just the
  Docker binaries.
- **Portainer / Dockge** are deployed as Docker containers (the standard
  way both projects recommend). "Install" = create the container/stack;
  "uninstall" = stop and remove it. Dockge's `/opt/stacks` directory
  (where your actual compose stacks live) is left untouched on uninstall.
- Tested against apt-based distros (Ubuntu/Debian). Other package
  managers (dnf, pacman, etc.) aren't handled — adjust `scripts/*.py` if
  you're on a different distro.

## Extending

To add another tool, create `scripts/your_tool.py` with the same
interface (`NAME`, `is_installed()`, `install()`, `uninstall()`) and add
it to the `TOOLS` list in `main.py`.


## License

MIT — see [LICENSE](LICENSE).
