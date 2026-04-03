# 🍳 Bacon Maker: How-To Guide

Practical guides for extending and testing your metadata-driven orchestration engine.

## How to add a new database dialect

To add support for a new database (e.g., Snowflake or BigQuery):

1.  **Update Type Mapping:**
    Open `bacon_maker/templating.py` and modify the `map_type()` function to include the new dialect's type mapping logic.
    ```python
    elif d == 'snowflake':
        if rt in ['NUMBER', 'FLOAT']: return "DECIMAL"
        return "STRING"
    ```

2.  **Add a Driver:**
    Update `requirements.txt` with the required Python driver (e.g., `snowflake-connector-python`) and create a new connection handler in the engine layer.

---

## How to write a custom Jinja template with loop logic

Bacon Maker supports complex logic inside steps. Here is an example of a `job.yaml` configuration using a loop to process multiple tables:

```yaml
job_id: "multi_table_migration"
parameters:
  target_schema: "ARCHIVE"
  tables: ["orders", "items", "customers"]
steps:
  - step_id: "archive_tables"
    transaction_enabled: true
    sql_templates:
      - name: "migration_loop"
        template_ref: |
          {% for table in tables %}
          INSERT INTO {{ target_schema }}.{{ table }}
          SELECT * FROM SOURCE_DB.{{ table }};
          {% endfor %}
```

---

## How to safely test with Chaos Monkey

Chaos Monkey ensures your system can handle non-deterministic failures without corrupting state.

1.  **Configure High Probability:**
    In your job configuration, set the `probability` to `1.0` to guarantee a failure during the next run.
    ```yaml
    chaos_monkey:
      enabled: true
      probability: 1.0
      error_codes:
        - error_code: 500
          description: "SIMULATED_DB_CRASH"
    ```

2.  **Verify Rollback:**
    Run the job using `execute_job`. Verify that for steps where `transaction_enabled: True`, the database remains unchanged despite the failure.

3.  **Audit Trace:**
    Check `job_trace.yaml` to confirm the step is marked as `FAILED` with the simulated error description.
