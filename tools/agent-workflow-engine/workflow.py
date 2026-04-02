#!/usr/bin/env python3
"""
Agent Workflow Engine
Orchestrates multi-step workflows across multiple agents.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class WorkflowEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.workflows_file = self.data_dir / "workflows.json"
        self.executions_file = self.data_dir / "workflow_executions.json"
        self.workflows = self._load_workflows()
        self.executions = self._load_executions()
    
    def _load_workflows(self):
        if self.workflows_file.exists():
            with open(self.workflows_file) as f:
                return json.load(f)
        return {"workflows": {}}
    
    def _load_executions(self):
        if self.executions_file.exists():
            with open(self.executions_file) as f:
                return json.load(f)
        return {"executions": []}
    
    def _save_workflows(self):
        with open(self.workflows_file, 'w') as f:
            json.dump(self.workflows, f, indent=2)
    
    def _save_executions(self):
        with open(self.executions_file, 'w') as f:
            json.dump(self.executions, f, indent=2)
    
    def create_workflow(self, name, steps, description=""):
        """Create a new workflow definition."""
        workflow_id = f"wf-{uuid.uuid4().hex[:8]}"
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "steps": steps,  # List of {name, agent_type, action, dependencies}
            "created": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.workflows["workflows"][workflow_id] = workflow
        self._save_workflows()
        return {"status": "created", "workflow_id": workflow_id, "workflow": workflow}
    
    def execute_workflow(self, workflow_id, context=None):
        """Execute a workflow with given context."""
        if workflow_id not in self.workflows["workflows"]:
            return {"error": "workflow not found"}
        
        workflow = self.workflows["workflows"][workflow_id]
        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "current_step": 0,
            "step_results": [],
            "context": context or {},
            "error": None
        }
        
        self.executions["executions"].append(execution)
        self._save_executions()
        
        return {"status": "started", "execution_id": execution_id}
    
    def get_execution(self, execution_id):
        """Get execution status and results."""
        for exec in self.executions["executions"]:
            if exec["id"] == execution_id:
                return exec
        return {"error": "execution not found"}
    
    def complete_step(self, execution_id, step_name, result):
        """Mark a step as completed."""
        for exec in self.executions["executions"]:
            if exec["id"] == execution_id:
                exec["step_results"].append({
                    "step": step_name,
                    "result": result,
                    "completed_at": datetime.utcnow().isoformat()
                })
                exec["current_step"] += 1
                
                # Check if workflow complete
                workflow = self.workflows["workflows"].get(exec["workflow_id"])
                if workflow and exec["current_step"] >= len(workflow["steps"]):
                    exec["status"] = "completed"
                    exec["completed_at"] = datetime.utcnow().isoformat()
                
                self._save_executions()
                return {"status": "step_completed"}
        
        return {"error": "execution not found"}
    
    def fail_execution(self, execution_id, error):
        """Mark execution as failed."""
        for exec in self.executions["executions"]:
            if exec["id"] == execution_id:
                exec["status"] = "failed"
                exec["error"] = str(error)
                exec["failed_at"] = datetime.utcnow().isoformat()
                self._save_executions()
                return {"status": "marked_failed"}
        
        return {"error": "execution not found"}
    
    def list_workflows(self):
        """List all workflows."""
        return list(self.workflows["workflows"].values())
    
    def list_executions(self, status=None):
        """List executions, optionally filtered."""
        execs = self.executions["executions"]
        if status:
            execs = [e for e in execs if e["status"] == status]
        return execs


def main():
    import sys
    engine = WorkflowEngine()
    
    if len(sys.argv) < 2:
        print("Agent Workflow Engine")
        print("Usage: workflow-engine.py <command> [args]")
        print("Commands:")
        print("  create <name> <steps_json> [description]")
        print("  list")
        print("  execute <workflow_id> [context_json]")
        print("  execution <execution_id>")
        print("  complete <execution_id> <step_name> <result_json>")
        print("  fail <execution_id> <error>")
        print("  executions [status]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "create":
        if len(sys.argv) < 4:
            print("Usage: create <name> <steps_json> [description]")
            return
        name = sys.argv[2]
        steps = json.loads(sys.argv[3])
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        result = engine.create_workflow(name, steps, desc)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        workflows = engine.list_workflows()
        print(json.dumps(workflows, indent=2))
    
    elif cmd == "execute":
        if len(sys.argv) < 3:
            print("Usage: execute <workflow_id> [context_json]")
            return
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
        result = engine.execute_workflow(sys.argv[2], context)
        print(json.dumps(result, indent=2))
    
    elif cmd == "execution":
        if len(sys.argv) < 3:
            print("Usage: execution <execution_id>")
            return
        result = engine.get_execution(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "complete":
        if len(sys.argv) < 5:
            print("Usage: complete <execution_id> <step_name> <result_json>")
            return
        result = json.loads(sys.argv[4])
        result = engine.complete_step(sys.argv[2], sys.argv[3], result)
        print(json.dumps(result, indent=2))
    
    elif cmd == "fail":
        if len(sys.argv) < 4:
            print("Usage: fail <execution_id> <error>")
            return
        result = engine.fail_execution(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2))
    
    elif cmd == "executions":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        result = engine.list_executions(status)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()