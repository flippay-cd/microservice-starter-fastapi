# Observability

## Local deployment ready
- Traces (done)
- Metrics (not done)
- Logs (done)

## Logging
- For logging, it is recommended to use [struct_log](https://www.structlog.org/en/stable/index.html)
- A good [talk about struct_log](https://conf.python.ru/moscow/2021/abstracts/8026) from Sber at PythonConf to get acquainted with `struct_log`
- The root logger of the standard library `logging` is also configured to output log in `json` with telemetry in context (trace_id, span_id, etc)
- Instrumentation using [json-logging-python](https://github.com/bobbui/json-logging-python) allows you to output logs in `json` format with additional information. Instruments `uvicorn` logs, adds timestamps and `request` info
