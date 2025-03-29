import os
from pathlib import Path
import shutil

REMOVE_PATHS = [
    {% if db == "no" %}
    '.helm/templates/migrations.yml',
    'backend/alembic',
    'backend/alembic.ini',
    'backend/app/tests/fixtures/db.py',
    {% endif %}
    {% if http_framework != "fastapi" %}
    'backend/app/uvicorn.dev.py',
    'backend/app/uvicorn.prod.py',
    {% endif %}
    {% if cache != "redis" and broker != "redis" %}
    'backend/app/infra/redis.py',
    {% endif %}
    {% if worker != "dramatiq" %}
    'backend/app/core/dramatiq',
    '.taskfiles/dramatiq',
    {% endif %}
    {% if event_bus_consumer != "faststream" %}
    '.helm/templates/faststream-inbox.yml',
    '.taskfiles/faststream',
    'backend/app/management/commands/faststream_inbox_cleanup.py',
    'backend/app/dal/tasks/inbox.py',
    'backend/app/streams',
    'backend/app/main_stream.py',
    {% endif %}
    {% if analytics != "clickhouse" %}
    'backend/app/infra/clickhouse_client.py',
    '.docs/clickhouse.md',
    {% endif %}
]

for path in REMOVE_PATHS:
    path = path.strip()
    # print(path)
    if path and os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)
