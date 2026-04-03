🚀 Bacon Maker: The MCP Meta-Orchestrator

Bacon Maker is a Metadata-First Orchestration Layer designed specifically for AI Agents. Using the Model Context Protocol (MCP), it acts as a secure, state-aware bridge between Large Language Models and complex database infrastructures (SQLite, MySQL, Teradata).

It is not just a script runner; it is a self-healing, linting, chaos-tested orchestration engine.

I. The Constitution (Guiding Principles)

Execution is State-Aware: A job is a stateful entity. The system must always know what succeeded, what failed, and where it can safely restart based on granular SQL-level traces.

Metadata over Hard-Coding: All logic (SQL generation, validation, environment config) must be derived from YAML/JSON files. The MCP server is a generic engine, not a collection of bespoke scripts.

Security by Redaction: The DOMAIN_ROLE is the ultimate filter. Unauthorized database objects are invisible to the Data Dictionary and the Template Renderer.

Lint-First Execution: No SQL touches the database unless it passes the mandatory validation pipeline (Jinja rendering -> SQLFluff linting), ensuring high code quality.

Resilience via Chaos: The system supports "Chaos Monkey" attributes to simulate non-deterministic failures, forcing AI agents to handle real-world instability.

Transparency via Artifacts: Every execution persists its "Resolved" state (Rendered SQL and Merged Metadata) to a temporary directory for auditing before/during execution.

II. Security & User Profiles

The system uses a strict YAML/JSON User Profile to define the agent's sandbox.

user_id: "agent_alpha_01"
name: "Bacon Maker Prod Agent"

# DOMAIN_ROLE: The Data Sandbox (Uses '%' wildcard)
domain_role:
  - database: "PROD_SALES%"
    schema: "%"
    table: "%"

# ACTION_ROLE: Functionality Permissions
action_role:
  - "DISCOVER"      # Access to query_dictionary, inspect_job
  - "DEVELOP"       # Access to dry_run_job, explain_sql
  - "EXECUTE"       # Access to execute_job (mode='run')
  - "RECOVER"       # Access to execute_job (mode='restart')



Enforcement: If a Jinja template resolves to an object not matched by domain_role, the rendering engine throws a SECURITY_VIOLATION_ERROR.

III. Metadata Hierarchy & Schema

Configuration flows downward: Environment $\rightarrow$ Domain $\rightarrow$ Job $\rightarrow$ Step.

Job Metadata Schema (job.yaml)

job_id: "string"               
job_name: "string"             
global_sql_validation: boolean 

chaos_monkey:                  
  enabled: boolean             
  probability: 0.1             
  error_codes:                 
    - { error_code: -1, description: "UNKNOWN_CHAOS_ERROR" }

parameters: { ... }            # Job-level variables

steps:                         
  - step_id: "string"          
    step_type: "SIMPLE"        # Can be SIMPLE or LOOP
    run_condition: "string"    # CEL: Evaluated before normal execution
    run_on_restart: "string"   # CEL: Evaluated ONLY during restart phase
    transaction_enabled: true  # Wraps SQL in BEGIN/COMMIT
    
    # If step_type == "LOOP", iterate over this list in the parameters
    loop_on: "parameter_list_name" 

    sql_templates:             
      - name: "string"         
        template_ref: "string" # Path to .jinja file
        lint_enabled: boolean  
        timeout_seconds: integer 
        max_rows: integer        
        validation_condition: "string" # CEL post-check
        restart_condition: "string"    # CEL restart check



IV. The Execution & Validation Pipeline

When execute_job is called, every SQL statement follows this lifecycle:

Context Merging: Merge Env + Domain + Job + Step parameters. (Injects restart_active boolean).

Artifact Generation: Render Jinja templates and write resolved YAML/SQL to job_tmp/<job_name>/.

Linting (SQLFluff): Validate rendered SQL in job_tmp/. Halt on critical errors.

Pre-Check (CEL): Evaluate run_condition (or run_on_restart if restart_active is True).

Chaos Injection: Evaluate Chaos Monkey probability. If triggered, skip execution and return simulated error.

Pre-Flight Check: Validate target tables against data_dictionary.yaml.

Execution: Dispatch to DB respecting timeout_seconds and transaction_enabled rules.

Post-Check (CEL): Evaluate validation_condition against DB results.

Trace Persistence: Update job_trace.yaml.

V. Reliability & State Management

1. Job Trace Schema (job_trace.yaml)

The engine is stateless; recovery relies entirely on this artifact.

job_id: "sales_load_2024"
status: "FAILED"
steps:
  step_02_load:
    status: "CHAOS_FAILURE"
    sql_executions:
      - name: "fact_insert"
        status: "CHAOS_FAILURE"
        error_code: -1
        injected_failure: true



2. Transactionality & Guardrails

Rollbacks: Any failure within a transaction_enabled step triggers an automatic DB ROLLBACK.

Limits: Long-running queries are killed if they exceed timeout_seconds. Massive selects are truncated by max_rows.

VI. Offline Mode & Dictionary Extraction

Bacon Maker operates an "Offline" metadata service so AI agents can brainstorm pipelines without hitting the database. The data_dictionary.yaml is populated using dialect-specific Jinja templates.

Data Type Normalization Macro

{% macro map_type(dialect, raw_type, length=none, precision=none, scale=none) %}
    {%- if dialect == 'teradata' -%}
        {%- if raw_type in ['I', 'I1', 'I2', 'I8'] -%} INTEGER
        {%- elif raw_type in ['D', 'F'] -%} DECIMAL({{ precision | default(18) }},{{ scale | default(2) }})
        {%- elif raw_type in ['CV', 'CF', 'CO'] -%} STRING({{ length }})
        {%- elif raw_type == 'DA' -%} DATE
        {%- else -%} UNKNOWN({{ raw_type }})
        {%- endif -%}
    {%- elif dialect == 'mysql' -%}
        {%- if 'int' in raw_type -%} INTEGER
        {%- elif 'char' in raw_type or 'text' in raw_type -%} STRING
        {%- else -%} {{ raw_type | upper }}
        {%- endif -%}
    {%- else -%} {{ raw_type | upper }}
    {%- endif -%}
{% endmacro %}



Extraction Queries

Teradata: SELECT ... FROM DBC.TablesV JOIN DBC.ColumnsV. Uses SHOW VIEW for exact logic extraction.

MySQL: SELECT ... FROM INFORMATION_SCHEMA.COLUMNS.

SQLite: PRAGMA table_info and sqlite_master.

VII. The MCP Toolset (API for AI Agents)

The server exposes these tools to the LLM:

query_dictionary(search): Search the offline YAML dictionary (respects DOMAIN_ROLE).

inspect_job(job_id): Return full metadata config and current trace status.

explain_sql(job_id, step_id, sql_name): Return the native DB execution plan (e.g., EXPLAIN SELECT...).

execute_job(job_id, mode=['run', 'restart'], chaos_override=null): Trigger the orchestration pipeline.

get_resolved_artifact(job_id, file_name): Read a file from the job_tmp directory for debugging.

VIII. Python Dependencies & Environment Setup

Bacon Maker requires a robust, async-ready Python environment. Coding agents must provision the following PyPI modules to satisfy the architectural requirements:

Core Orchestration & MCP

mcp: The official Model Context Protocol Python SDK for exposing tools to AI agents.

pydantic: For strict schema validation of User Profiles and Job Metadata.

PyYAML: For parsing and persisting YAML artifacts and traces.

python-dotenv: For securely loading local .env files into the application's environment variables.

Credential Management (.env)

For the testing and development phase, sensitive credentials (like database passwords) must never be hard-coded or stored in the plain-text YAML/JSON metadata files.

.env File: Use a local .env file to store credentials as environment variables (e.g., TERADATA_PWD=secret). Ensure this file is added to your .gitignore.

Dynamic Lookup: The MCP server will use the connection_id defined in the Job Environment YAML to dynamically look up the corresponding password from the environment variables at runtime using os.getenv().

Initialization: Coding agents should use python-dotenv's load_dotenv() function to load these variables securely into the server environment upon startup.

Template & Evaluation Engines

Jinja2: The core engine for resolving parameters into SQL logic.

cel-python (or cel-expr-python/common-expression-language): A Python evaluator for Google's Common Expression Language to process run_condition and validation_condition logic securely.

Linting & Guardrails

sqlfluff: The automated SQL linter to act as the pre-flight gatekeeper before database execution.

Database Drivers

teradatasql: For connecting to Teradata infrastructure.

mysql-connector-python (or PyMySQL): For MySQL dialect connectivity.

sqlite3: (Standard Library) For lightweight, file-based mock databases.

Development & Testing

pytest & pytest-asyncio: For executing the strict agent testing criteria (since MCP servers operate asynchronously).

IX. Implementation Requirements for Coding Agents

Strict Parsers: Use pydantic to validate all incoming YAML/JSON configuration files.

CEL Sandbox: The CEL evaluator must treat the trace and results objects as immutable contexts.

Clean State: The job_tmp/ directory must be wiped completely at the start of every new execute_job command unless explicitly skipped.

X. Coding Agent Testing Criteria

To ensure Bacon Maker is rock-solid, coding agents must build a comprehensive automated test suite. "Test, test, and more test" is the rule. The following criteria must be proven with automated tests:

1. Unit Testing (The Fundamentals)

Schema Validation: Test JSON/YAML parsers against valid and intentionally malformed job.yaml and user_profile.yaml configurations.

CEL Logic: Test the evaluator with mocked trace payloads to ensure run_condition and run_on_restart correctly skip or trigger steps.

Dialect Rendering: Test the Jinja map_type macro to guarantee correct translation of raw data types across SQLite, MySQL, and Teradata logic.

2. Integration Testing (The Pipeline)

End-to-End Mock Run: Execute a multi-step job against an in-memory SQLite database. Assert that artifacts write successfully to job_tmp/ and the final job_trace.yaml reports SUCCESS.

Linting Gates: Inject syntactically invalid SQL into a test template and verify that SQLFluff correctly catches the error and halts the pipeline before DB execution.

Transaction Integrity: Force a failure on step 2 of a 3-step transaction_enabled job. Query the test database to ensure step 1's operations were successfully ROLLED BACK.

3. Security & Chaos Testing (The Edge Cases)

The Sandbox Test: Attempt to extract metadata or render a template for a database outside the mock agent's DOMAIN_ROLE. Assert that a SECURITY_VIOLATION_ERROR is thrown.

The Chaos Monkey Test: Trigger a job with a 1.0 (100%) chaos probability. Assert that the database remains untouched, the trace logs CHAOS_FAILURE, and the injected_failure flag is true.

The Recovery Test: Following a simulated failure, re-run the job with mode='restart'. Assert that it successfully skips previously completed steps, executes the run_on_restart logic, and resumes execution properly.

XI. Interactive Testing (MCP Inspector)

Beyond automated unit testing, developers and AI agents must be able to interactively test the MCP server tools just as an LLM would. This is done using the official MCP Inspector utility (npx).

To spin up the local web-based testing UI, run the following command (requires Node.js to be installed):

npx @modelcontextprotocol/inspector python -m bacon_maker_server
# Alternatively, if running a specific script directly:
# npx @modelcontextprotocol/inspector python main.py



This will provide a GUI where you can manually invoke execute_job, query_dictionary, and other tools, viewing the direct JSON responses returned by the MCP server.

XII. Documentation & Maintenance Requirements

Code is only as good as its documentation. Coding agents and human developers must adhere to the following documentation standards at all times:

Living Documentation: This README.md and all inline code documentation must be kept strictly up to date. Any new feature, schema change, or architectural pivot must be documented concurrently with the code change.

Reference & How-To Manual: A dedicated docs/ directory must be established and maintained. It must contain at minimum:

Reference Manual: Detailed breakdowns of all Jinja contexts, CEL functions, MCP tool definitions, and YAML schema properties.

How-To Manual: Step-by-step guides covering common tasks, such as: "How to add a new database dialect," "How to create a new job domain," and "How to write a custom Jinja template with loop logic."

Version Control: Documentation updates must be included in the same git commits as the code changes they describe.

XIII. Phased Development Plan

To ensure a robust, test-driven implementation, coding agents must follow this phased build approach:

Phase 0: Environment Setup (The Foundation)

Goal: Create a clean, reproducible Python environment.

Tasks: Initialize a Python virtual environment (e.g., venv), set up .env for secure credential loading, install all required dependencies (MCP SDK, Pydantic, Jinja2, SQLFluff, Pytest), and configure .gitignore.

Testing Gate: Verify virtual environment activates correctly and all dependencies import cleanly.

Phase 1: Foundations & Configuration (The Data Layer)

Goal: Setup strict schema validation.

Tasks: Create Pydantic models for the Job Schema and User Profile exactly as defined in the Constitution.

Testing Gate: Unit tests parsing valid and invalid YAML files.

Phase 2: The Template Engine & Linting (The Logic Layer)

Goal: Build the secure Jinja environment and SQL validation.

Tasks: Implement Jinja2 rendering (with the map_type macro), integrate sqlfluff for validation, and implement the job_tmp/ artifact wiping/persistence logic.

Testing Gate: Render a mock template, persist it, and pass it through the linter.

Phase 3: Evaluators & Security (The Guardrails)

Goal: Implement CEL rules and DOMAIN_ROLE enforcement.

Tasks: Setup cel-python to evaluate runtime/restart conditions and build the security filter that throws SECURITY_VIOLATION_ERROR for unauthorized objects.

Testing Gate: Sandbox testing to ensure unauthorized objects are strictly blocked.

Phase 4: The Orchestrator & State (The Engine)

Goal: Core execution loop and trace management.

Tasks: Build the step executor managing transaction_enabled rollbacks and timeouts, implement job_trace.yaml persistence, and introduce Chaos Monkey logic.

Testing Gate: End-to-end multi-step mock job against SQLite, successfully forcing a rollback and a Chaos failure.

Phase 5: The MCP Server Interface (The Bridge)

Goal: Expose the engine to external agents.

Tasks: Wrap the tested engine in the official mcp Python SDK and expose tools (query_dictionary, inspect_job, explain_sql, execute_job).

Testing Gate: Interactive testing using the npx @modelcontextprotocol/inspector.