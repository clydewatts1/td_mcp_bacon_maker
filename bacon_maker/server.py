import os
import yaml
import sqlite3
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

from bacon_maker.engine import execute_job as run_engine
from bacon_maker.state import JobTrace
from bacon_maker.templating import render_sql
from bacon_maker.security import enforce_domain_role
from bacon_maker.artifacts import BASE_TMP_DIR

# Initialize the FastMCP server
mcp = FastMCP("BaconMaker")

@mcp.tool()
def query_dictionary(search_pattern: str, domain_roles: List[str]) -> Dict[str, Any]:
    """
    Searches the offline data_dictionary.yaml while respecting the agent's DOMAIN_ROLE.
    Returns a filtered list of tables and columns matching the pattern.
    """
    dict_path = "data_dictionary.yaml"
    if not os.path.exists(dict_path):
        return {"error": "data_dictionary.yaml not found."}
        
    with open(dict_path, "r", encoding="utf-8") as f:
        data_dict = yaml.safe_load(f) or {}
        
    results = {}
    for table_name, details in data_dict.items():
        # Respect Security Sandbox (Phase 3)
        try:
            if search_pattern.upper() in table_name.upper():
                enforce_domain_role(table_name, domain_roles)
                results[table_name] = details
        except Exception:
            continue # Skip unauthorized objects
            
    return {"matches": results}

@mcp.tool()
def inspect_job(job_id: str) -> Dict[str, Any]:
    """
    Returns the job's current trace status from job_trace.yaml.
    """
    trace_path = os.path.join(BASE_TMP_DIR, job_id, "job_trace.yaml")
    if not os.path.exists(trace_path):
        return {"error": f"Trace for job '{job_id}' not found."}
        
    with open(trace_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@mcp.tool()
def explain_sql(job_id: str, step_id: str, sql_name: str, context: Dict[str, Any]) -> str:
    """
    Renders the requested SQL template and simulates fetching the native DB execution plan.
    """
    # Note: In a real implementation, we'd lookup the template in the job metadata.
    # For this interface, we assume the template snippet is part of the context or found.
    # We simulate by returning the rendered SQL prefixed with EXPLAIN.
    
    # Mock template lookup - we'll just render it for now
    rendered_sql = render_sql("SELECT * FROM my_table;", context) # Simplified example
    return f"EXPLAIN {rendered_sql}"

@mcp.tool()
def execute_job(job_id: str, mode: str = 'run', chaos_override: float = None) -> Dict[str, Any]:
    """
    Triggers the core orchestrator pipeline built in Phase 4.
    """
    # Mock configuration lookup - in reality we'd pull from a store
    mock_job_config = {
        "job_id": job_id,
        "job_name": f"MCP Triggered Job {job_id}",
        "steps": [
            {
                "step_id": "step_01",
                "transaction_enabled": True,
                "sql_templates": [
                    {"name": "hello_mcp", "template_ref": "SELECT 'Hello from MCP!' as msg;", "lint_enabled": False}
                ]
            }
        ],
        "chaos_monkey": {"enabled": (chaos_override is not None), "probability": chaos_override or 0.0}
    }
    
    # In-memory SQLite for demo/testing via MCP
    conn = sqlite3.connect(":memory:")
    try:
        trace = run_engine(mock_job_config, conn, mode=mode)
        return trace
    finally:
        conn.close()

@mcp.tool()
def get_resolved_artifact(job_id: str, file_name: str) -> str:
    """
    Reads and returns the contents of a specific file from the job_tmp/<job_name> directory.
    """
    file_path = os.path.join(BASE_TMP_DIR, job_id, file_name)
    if not os.path.exists(file_path):
        return f"Error: Artifact '{file_name}' for job '{job_id}' not found."
        
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
