import os
import yaml
from typing import Any, Dict

def save_trace(job_id: str, trace_data: Dict[str, Any]):
    """
    Persists the current job execution state to job_tmp/<job_id>/job_trace.yaml.
    As defined in the Constitution Section V.
    """
    job_dir = os.path.join("job_tmp", job_id)
    if not os.path.exists(job_dir):
        os.makedirs(job_dir, exist_ok=True)
        
    trace_path = os.path.join(job_dir, "job_trace.yaml")
    
    with open(trace_path, "w", encoding="utf-8") as f:
        yaml.dump(trace_data, f, default_flow_style=False)
    
    return trace_path

class JobTrace:
    """Helper class to build and maintain the state of a job execution."""
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.trace = {
            "job_id": job_id,
            "status": "STARTED",
            "steps": {}
        }

    def update_step(self, step_id: str, status: str, details: Dict[str, Any] = None):
        if step_id not in self.trace["steps"]:
            self.trace["steps"][step_id] = {"status": status, "templates": []}
        else:
            self.trace["steps"][step_id]["status"] = status
            
        if details:
            self.trace["steps"][step_id].update(details)
        save_trace(self.job_id, self.trace)

    def add_template_result(self, step_id: str, template_name: str, status: str, error: str = None):
        res = {"name": template_name, "status": status}
        if error:
            res["error"] = error
        self.trace["steps"][step_id]["templates"].append(res)
        save_trace(self.job_id, self.trace)

    def finalize(self, status: str):
        self.trace["status"] = status
        save_trace(self.job_id, self.trace)
