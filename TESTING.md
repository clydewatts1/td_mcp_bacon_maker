# 🛠️ Bacon Maker: Testing & Inspection

Bacon Maker uses the **Model Context Protocol (MCP)** to expose its orchestration tools. To interactively test the server, you can use the official MCP Inspector.

## Prerequisites
- **Node.js** must be installed.
- **Python environment** must be activated (`.\venv\Scripts\activate`).

## Launching the Inspector

Run the following command from the project root:

```bash
npx @modelcontextprotocol/inspector python -m bacon_maker
```

This will launch a local web browser UI where you can:
1.  **View Tools:** See the list of 5 available tools (`query_dictionary`, `execute_job`, etc.).
2.  **Call Tools:** Manually input JSON arguments and see the direct responses from the engine.
3.  **Audit Logs:** View the JSON-RPC traffic between the inspector and the Bacon Maker server.

## Available Tools
- `query_dictionary`: Secured metadata search using `DOMAIN_ROLE`.
- `inspect_job`: Get the current `job_trace.yaml` for a job ID.
- `execute_job`: Run a core orchestration loop.
- `explain_sql`: Render and audit SQL before execution.
- `get_resolved_artifact`: Retrieve specific rendered SQL files.
