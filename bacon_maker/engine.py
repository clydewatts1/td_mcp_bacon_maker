import sqlite3
import time
from typing import Any, Dict, List
from bacon_maker.evaluator import evaluate_condition
from bacon_maker.templating import render_sql
from bacon_maker.linting import validate_sql
from bacon_maker.artifacts import setup_job_directory, write_artifact
from bacon_maker.state import JobTrace
from bacon_maker.chaos import evaluate_chaos

def execute_job(job_config: Dict[str, Any], db_conn: sqlite3.Connection, mode: str = 'run') -> Dict[str, Any]:
    """
    Main orchestration loop for executing a multi-step job.
    As defined in the Constitution Section IV.
    """
    job_id = job_config["job_id"]
    job_trace = JobTrace(job_id)
    
    # 1. Setup fresh artifact directory
    setup_job_directory(job_id)
    
    # Context for CEL evaluation (includes global parameters)
    context = {
        "parameters": job_config.get("parameters", {}),
        "trace": job_trace.trace,
        "restart_active": (mode == 'restart')
    }

    try:
        for step in job_config.get("steps", []):
            step_id = step["step_id"]
            
            # 2. Check run conditions
            condition = step.get("run_condition") if mode == 'run' else step.get("run_on_restart")
            if not evaluate_condition(condition, context):
                job_trace.update_step(step_id, "SKIPPED")
                continue
            
            job_trace.update_step(step_id, "RUNNING")
            
            # 3. Transaction management (Step Level)
            if step.get("transaction_enabled"):
                db_conn.execute("BEGIN TRANSACTION")
            
            try:
                for tpl in step.get("sql_templates", []):
                    tpl_name = tpl["name"]
                    
                    # 4. Chaos Monkey Check
                    chaos_error = evaluate_chaos(job_config.get("chaos_monkey"))
                    if chaos_error:
                        job_trace.add_template_result(step_id, tpl_name, "CHAOS_FAILURE", error=chaos_error["description"])
                        raise Exception(f"Chaos Monkey Injection: {chaos_error['description']}")

                    # 5. Rendering & Persistence
                    sql = render_sql(tpl["template_ref"], context)
                    write_artifact(job_id, f"{step_id}_{tpl_name}.sql", sql)
                    
                    # 6. Linting
                    if tpl.get("lint_enabled"):
                        lint_res = validate_sql(sql)
                        if not lint_res["is_valid"]:
                            job_trace.add_template_result(step_id, tpl_name, "LINT_FAILURE")
                            raise Exception(f"SQL Lint failure in {tpl_name}")

                    # 7. Execution
                    cursor = db_conn.cursor()
                    cursor.execute(sql)
                    
                    job_trace.add_template_result(step_id, tpl_name, "SUCCESS")

                # 8. Commit Step Transaction
                if step.get("transaction_enabled"):
                    db_conn.commit()
                job_trace.update_step(step_id, "SUCCESS")

            except Exception as e:
                # 9. Rollback on Failure
                if step.get("transaction_enabled"):
                    db_conn.rollback()
                job_trace.update_step(step_id, "FAILED", {"error": str(e)})
                raise e # Propagate to halt job

        job_trace.finalize("SUCCESS")
        return job_trace.trace

    except Exception as e:
        job_trace.finalize("FAILED")
        return job_trace.trace
