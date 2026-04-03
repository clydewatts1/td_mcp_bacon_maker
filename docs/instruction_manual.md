# 🥓 Bacon Maker: Technical Reference Manual

This manual provides a detailed breakdown of the Bacon Maker orchestrator's internals, tool definitions, and metadata structures.

## 🛠️ MCP Tool Definitions

Bacon Maker exposes the following core tools over the Model Context Protocol:

### 1. `query_dictionary(search_pattern: str, domain_roles: list)`
*   **Purpose:** Searches the offline `data_dictionary.yaml` for database objects matching the pattern.
*   **Security:** Automatically filters results based on the provided `DOMAIN_ROLE` wildcard patterns.
*   **Input:** `search_pattern` (e.g., "SALES"), `domain_roles` (list of patterns like "PROD_%").
*   **Output:** JSON object containing matching tables and column metadata.

### 2. `inspect_job(job_id: str)`
*   **Purpose:** Retrieves the real-time execution trace of a specific job.
*   **Input:** `job_id` (unique string).
*   **Output:** The full contents of `job_trace.yaml`, showing step-level and template-level success/failure states.

### 3. `explain_sql(job_id: str, step_id: str, sql_name: str, context: dict)`
*   **Purpose:** Renders a SQL template and simulates a database "EXPLAIN" for audit and planning.
*   **Input:** Identifiers for the job/step/template and the runtime context variables.
*   **Output:** The fully rendered SQL string prefixed with `EXPLAIN`.

### 4. `execute_job(job_id: str, mode: str, chaos_override: float)`
*   **Purpose:** Triggers the multi-step orchestration pipeline.
*   **Input:** `mode` ('run' for fresh execution, 'restart' for recovery), `chaos_override` (optional probability).
*   **Output:** The final `JobTrace` object reflecting the outcome.

### 5. `get_resolved_artifact(job_id: str, file_name: str)`
*   **Purpose:** Retrieves a specific rendered artifact (SQL or YAML) produced during execution.
*   **Input:** `job_id` and the specific file name (e.g., "step_01_create_table.sql").
*   **Output:** The raw file contents.

---

## 🏗️ Metadata & Schema Properties

### User Profile (`user_profile.yaml`)
Enforces the security sandbox for the agent.
- `user_id`: Unique identifier for the agent.
- `domain_role`: List of patterns defining authorized database objects (e.g., `["PROD_DB.%", "DEV_DB.%"]`).
- `action_role`: List of authorized action types (e.g., `["READ", "WRITE", "ADMIN"]`).

### Job Metadata (`job.yaml`)
Defined via Pydantic in `bacon_maker/schemas.py`.
- `job_id`: Unique job identifier.
- `steps`: List of Step objects.
    - `step_id`: Unique identifier for the step.
    - `transaction_enabled`: If True, issues BEGIN/COMMIT/ROLLBACK for the step.
    - `run_condition`: CEL expression for standard execution.
    - `run_on_restart`: CEL expression for recovery execution.
- `chaos_monkey`:
    - `enabled`: Global toggle for failure injection.
    - `probability`: Float (0.0 - 1.0) defining failure frequency.
    - `error_codes`: List of objects containing `error_code` and `description`.

---

## 🏎️ Logic & Engine Contexts

### Context Merging
Variables are merged in the following priority (highest first):
1. **Step Parameters:** Variables defined specifically for the current step.
2. **Job Parameters:** Global parameters defined at the top level of the job config.
3. **Environment:** System-level configurations (e.g., `dialect`).

### CEL Guardrails
CEL (Common Expression Language) expressions have access to:
- `parameters`: All job and step variables.
- `trace`: The current `JobTrace` object, allowing for logic like `trace.steps.step_01.status == 'SUCCESS'`.
- `restart_active`: Boolean flag indicating if the job is in 'restart' mode.

### Jinja Environment
- **Security:** Autoescaping enabled for HTML/XML contexts.
- **Normalization:** The `map_type()` macro is globally available for dialect-agnostic data typing.
