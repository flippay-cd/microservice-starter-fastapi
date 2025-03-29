# Development

### Working with the service
* The "repository" pattern is proposed as an architecture
* Three layers are clearly distinguished:
* Controllers (api endpoints)
* Business logic services (services)
* Data layer (dal)
* The project configuration is located in the `/core` directory
* The `dependency-injector` library is used to configure dependencies
* Dependencies are configured in `core/container.py`
* Keys/variables for the project are pulled from `.env` or environment variables

### Working with migrations
* Alembic is used to work with migrations
* Frequently used commands are available in `Taskfile.yml` - `task --list | grep "db:migrations:"`
* It should be noted that autodetect in Alembic does not detect all types of changes in models, so migrations should be checked manually before execution. [More](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)

### Checking migrations
Detailed description:
```bash
$ python -m check_migrations --help
```
Using in CI/CD pipelines:
```bash
$ task db:migrations:check:ci
```
Using in local development:
```bash
$ task db:migrations:check
```
Using before running migrations:
```bash
$ task db:migrations:check:pre-migrate
$ task db:migrations:upgrade
```

### Working with uv
* The main (high-level) dependencies are specified in `pyproject.toml`
* You can generate an output file with all dependencies using the command `task python:requirements:lock`
* You can synchronize installed packages with the project packages using the command `task python:requirements:sync`
* You can perform both previous actions using a single command `task python:requirements`

### Linters, formatters, pre-commit
* The main tool for code quality control is Ruff.
* Ruff is configured by including rules in pyproject.toml. Replaces isort and flake8.
* To enable pre-commit, you need to run `pre-commit install`

### Tests
* Run tests `task run:tests`
* View coverage: `coverage run -m pytest`, then `coverage report` or `coverage html`

### API generation
* Run `task setup:openapi`
* Commit the generated code
* If the openapi scheme changes, re-generate
* Generated code **never change manually**

### Working with GitLab CI and Helm Chart
* Run `task werf:helm:add` to add a helm chart to the project
* The token for this command can be taken from the previous point, i.e. `DOCKER_GITLAB_TOKEN`
* Run `task werf:helm:update` and commit the resulting `Chart.lock` file
* Fill in `values.yaml` if needed. [Documentation on available values ​​and default values](https://gitlab.tripster.ru/experience/helm-tripster-app)
* If secret-values.yaml is used, then generate a key using the `task werf:helm:generate-secret` command and insert its value (from the `.werf_secret_key` file) into the CI/CD variable `WERF_SECRET_KEY` in the settings in GitLab
* Fill in `secret-values.yaml` if needed. `task werf:helm:secret:edit:staging` and `task werf:helm:secret:edit:production`
* Documentation for .gitlab-ci.yml can be found [here](https://gitlab.tripster.ru/experience/ci-templates/-/blob/main/README.md)
