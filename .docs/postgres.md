## Deploy MR to a separate Postgres Schema

* To deploy MR to a separate Postgres schema, you need to edit the `values.yaml` file by adding the following lines to each deployment:

```yaml
postgres:
multitenancy: true
```
