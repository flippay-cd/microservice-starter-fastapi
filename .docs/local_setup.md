## Starting the project

### Initial environment setup

- Install Docker
- MacOS: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/desktop/install/linux-install/
- Make sure `docker` runs without `sudo`

- Install [Task](https://taskfile.dev)
- MacOS: `brew install go-task`
- Linux: `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin`
- Install autocomplete for task: https://taskfile.dev/installation/#option-1-load-the-completions-in-your-shells-startup-config-recommended

- Install [Werf](https://werf.io/)
- MacOS: `brew install werf`
- Linux: `curl -sSL https://werf.io/install.sh | bash -s -- --version 2 --channel stable`

- Install [uv](https://docs.astral.sh/uv/)
- MacOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Project local, infrastructure in Docker
- Install Python of the appropriate version for the project `uv python install <version, e.g. 3.13>`
- Create and activate a virtual environment
- Run `task run:backend:dev`
