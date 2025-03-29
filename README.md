# {{ project_name }}

## Description

<Project Description>

## Project Template

- download [copier](https://copier.readthedocs.io/en/stable/#installation) into your system

### Creating a new project from the template

`copier copy --trust "git@github.com:flippay-cd/microservice-starter-fastapi.git" ./`

### Update project from the template

`copier update --trust --defaults`

## Documentation

* [Setups](./.docs/local_setup.md)
* [Development](./.docs/development.md)
* [Github](./.docs/github.md)


### Infrastructure
* [Postgres](./.docs/postgres.md)
* [HTTP](./.docs/http.md)
{% if analytics != "clickhouse" %}* [Clickhouse](./.docs/clickhouse.md){% endif %}
