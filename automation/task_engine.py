#!/usr/bin/env python3
"""
TASK AUTOMATION ENGINE - Automate repetitive agent tasks
Purpose: Let agents define, schedule, and execute task pipelines automatically
"""
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path
from threading import Thread
import hashlib

class TaskTemplate:
    """Reusable task templates for common operations"""
    
    TEMPLATES = {
        "research_sweep": {
            "name": "Research Sweep",
            "description": "Research multiple topics in parallel",
            "steps": [
                {"action": "search", "query": "{topic}"},
                {"action": "summarize", "input": "search_results"},
                {"action": "extract_key_findings", "input": "summary"},
                {"action": "save_to_knowledge_graph", "input": "findings"}
            ],
            "params": ["topics"]
        },
        "code_review": {
            "name": "Code Review Pipeline",
            "description": "Review code for quality, security, and style",
            "steps": [
                {"action": "parse_code", "input": "{file_path}"},
                {"action": "check_quality", "input": "parsed_code"},
                {"action": "check_security", "input": "parsed_code"},
                {"action": "check_style", "input": "parsed_code"},
                {"action": "generate_report", "input": ["quality", "security", "style"]}
            ],
            "params": ["file_path"]
        },
        "deploy_service": {
            "name": "Service Deployment",
            "description": "Deploy a service from code to running",
            "steps": [
                {"action": "build", "input": "{code_path}"},
                {"action": "test", "input": "built_artifact"},
                {"action": "stage", "input": "passed_tests"},
                {"action": "deploy", "input": "staged_artifact"},
                {"action": "verify", "input": "deployed_service"}
            ],
            "params": ["code_path", "environment"]
        },
        "knowledge_sync": {
            "name": "Knowledge Sync",
            "description": "Sync knowledge between graph and external sources",
            "steps": [
                {"action": "read_local_graph", "input": None},
                {"action": "fetch_external", "input": "{source}"},
                {"action": "merge_knowledge", "input": ["local", "external"]},
                {"action": "resolve_conflicts", "input": "merged"},
                {"action": "save_to_graph", "input": "resolved"}
            ],
            "params": ["source"]
        }
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[Dict]:
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        return list(cls.TEMPLATES.keys())


class TaskPipeline:
    """Execute a series of steps as a pipeline"""
    
    def __init__(self, name: str, steps: List[Dict], params: Dict):
        self.id = self._generate_id()
        self.name = name
        self.steps = steps
        self.params = params
        self.status = "pending"
        self.results = {}
        self.logs = []
        self.started_at = None
        self.completed_at = None
    
    def _generate_id(self) -> str:
        return f"pipeline_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    def execute(self, context: Dict) -> Dict:
        """Execute the pipeline"""
        self.started_at = datetime.utcnow().isoformat()
        self.status = "running"
        self.log("Pipeline started")
        
        data = context.copy()
        data.update(self.params)
        
        for i, step in enumerate(self.steps):
            self.log(f"Executing step {i+1}/{len(self.steps)}: {step.get('action')}")
            
            action = step.get("action")
            input_ref = step.get("input")
            
            # Resolve input from previous results
            if input_ref and isinstance(input_ref, str) and input_ref.startswith("{"):
                # Parameter reference
                input_data = data.get(input_ref.strip("{}"), "")
            elif input_ref and isinstance(input_ref, str) and input_ref in self.results:
                input_data = self.results[input_ref]
            elif input_ref == "search_results":
                input_data = data.get("search_results", [])
            elif input_ref == "summary":
                input_data = data.get("summary", "")
            elif input_ref is None:
                input_data = None
            else:
                input_data = data.get(input_ref, input_ref)
            
            # Execute step (simulated - in real system would call actual actions)
            result = self._execute_step(action, input_data)
            self.results[action] = result
            
            # Check for failure
            if isinstance(result, dict) and result.get("error"):
                self.status = "failed"
                self.log(f"Step {i+1} failed: {result['error']}")
                return {"status": "failed", "results": self.results}
        
        self.status = "completed"
        self.completed_at = datetime.utcnow().isoformat()
        self.log("Pipeline completed successfully")
        
        return {"status": "completed", "results": self.results}
    
    def _execute_step(self, action: str, input_data) -> Dict:
        """Execute a single step"""
        try:
            if action == "search":
                return {"query": input_data, "results": [], "count": 0}
            elif action == "summarize":
                return {"summary": f"Summary of: {input_data}", "key_points": []}
            elif action == "extract_key_findings":
                return {"findings": [], "confidence": 0.8}
            elif action == "save_to_knowledge_graph":
                return {"saved": True, "node_id": "generated"}
            elif action == "parse_code":
                return {"parsed": True, "functions": [], "classes": []}
            elif action == "check_quality":
                return {"score": 0.85, "issues": []}
            elif action == "check_security":
                return {"vulnerabilities": [], "severity": "none"}
            elif action == "check_style":
                return {"compliant": True, "violations": []}
            elif action == "generate_report":
                return {"report": "Generated report", "format": "markdown"}
            elif action == "build":
                return {"artifact": "built.bin", "success": True}
            elif action == "test":
                return {"tests_passed": 10, "tests_failed": 0}
            elif action == "stage":
                return {"staged": True, "url": "staging.example.com"}
            elif action == "deploy":
                return {"deployed": True, "url": "prod.example.com"}
            elif action == "verify":
                return {"verified": True, "health": "healthy"}
            elif action == "read_local_graph":
                return {"nodes": [], "edges": []}
            elif action == "fetch_external":
                return {"data": [], "source": "external"}
            elif action == "merge_knowledge":
                return {"merged": True, "conflicts": []}
            elif action == "resolve_conflicts":
                return {"resolved": True, "method": "latest_wins"}
            else:
                return {"result": f"Executed {action}", "success": True}
        except Exception as e:
            return {"error": str(e)}
    
    def log(self, message: str):
        """Add log entry"""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        })
    
    def get_status(self) -> Dict:
        """Get pipeline status"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "steps_completed": len(self.results),
            "total_steps": len(self.steps),
            "logs": self.logs[-10:]  # Last 10 logs
        }


class TaskScheduler:
    """Schedule and run tasks automatically"""
    
    def __init__(self):
        self.scheduled_tasks = []
        self.running_pipelines = {}
        self.completed_pipelines = []
        self.data_dir = Path("/root/.openclaw/workspace/agent-hub/data")
        self._load_state()
    
    def _load_state(self):
        """Load scheduler state from disk"""
        state_file = self.data_dir / "scheduler_state.json"
        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)
                self.scheduled_tasks = state.get("scheduled_tasks", [])
                self.completed_pipelines = state.get("completed_pipelines", [])
    
    def _save_state(self):
        """Save scheduler state to disk"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        state_file = self.data_dir / "scheduler_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                "scheduled_tasks": self.scheduled_tasks,
                "completed_pipelines": self.completed_pipelines[-100:]  # Keep last 100
            }, f, indent=2)
    
    def schedule_task(self, name: str, template_name: str, params: Dict, 
                      interval: Optional[int] = None, 
                      cron: Optional[str] = None) -> str:
        """Schedule a task for execution"""
        task_id = f"task_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        task = {
            "id": task_id,
            "name": name,
            "template": template_name,
            "params": params,
            "interval": interval,  # seconds
            "cron": cron,
            "next_run": self._calculate_next_run(interval, cron),
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.scheduled_tasks.append(task)
        self._save_state()
        
        return task_id
    
    def _calculate_next_run(self, interval: Optional[int], cron: Optional[str]) -> str:
        """Calculate next run time"""
        if interval:
            next_time = datetime.utcnow() + timedelta(seconds=interval)
            return next_time.isoformat()
        elif cron:
            # Simple cron parsing (just hour:minute for now)
            return datetime.utcnow().isoformat()  # Placeholder
        else:
            return datetime.utcnow().isoformat()
    
    def run_task(self, task_id: str, context: Dict = None) -> Dict:
        """Run a scheduled task immediately"""
        task = None
        for t in self.scheduled_tasks:
            if t["id"] == task_id:
                task = t
                break
        
        if not task:
            return {"error": "Task not found"}
        
        template = TaskTemplate.get_template(task["template"])
        if not template:
            return {"error": f"Template {task['template']} not found"}
        
        pipeline = TaskPipeline(task["name"], template["steps"], task["params"])
        result = pipeline.execute(context or {})
        
        self.running_pipelines[pipeline.id] = pipeline
        
        # Move to completed
        if result["status"] == "completed":
            self.completed_pipelines.append({
                "id": pipeline.id,
                "task_id": task_id,
                "name": task["name"],
                "completed_at": pipeline.completed_at,
                "results": result.get("results", {})
            })
            self._save_state()
        
        return result
    
    def check_due_tasks(self) -> List[Dict]:
        """Check for tasks that are due to run"""
        now = datetime.utcnow()
        due_tasks = []
        
        for task in self.scheduled_tasks:
            if task["status"] != "scheduled":
                continue
            
            next_run = datetime.fromisoformat(task["next_run"])
            if next_run <= now:
                due_tasks.append(task)
        
        return due_tasks
    
    def run_due_tasks(self, context: Dict = None) -> List[Dict]:
        """Run all due tasks"""
        results = []
        for task in self.check_due_tasks():
            result = self.run_task(task["id"], context)
            results.append({
                "task_id": task["id"],
                "name": task["name"],
                "result": result
            })
            
            # Update next run time
            if task["interval"]:
                task["next_run"] = (datetime.utcnow() + timedelta(seconds=task["interval"])).isoformat()
        
        self._save_state()
        return results
    
    def list_tasks(self) -> List[Dict]:
        """List all scheduled tasks"""
        return self.scheduled_tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        for i, task in enumerate(self.scheduled_tasks):
            if task["id"] == task_id:
                task["status"] = "cancelled"
                self._save_state()
                return True
        return False


class TaskAutomationEngine:
    """Main engine for task automation"""
    
    def __init__(self):
        self.scheduler = TaskScheduler()
        self.templates = TaskTemplate()
        self.results_history = []
    
    def create_pipeline(self, name: str, template_name: str, params: Dict) -> str:
        """Create a new pipeline from template"""
        template = TaskTemplate.get_template(template_name)
        if not template:
            return None
        
        pipeline = TaskPipeline(name, template["steps"], params)
        return pipeline.id
    
    def schedule(self, name: str, template_name: str, params: Dict,
                 interval: Optional[int] = None) -> str:
        """Schedule a task"""
        return self.scheduler.schedule_task(name, template_name, params, interval)
    
    def run_now(self, task_id: str, context: Dict = None) -> Dict:
        """Run a task immediately"""
        return self.scheduler.run_task(task_id, context)
    
    def run_due(self, context: Dict = None) -> List[Dict]:
        """Run all due tasks"""
        return self.scheduler.run_due_tasks(context)
    
    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            "scheduled_tasks": len(self.scheduler.scheduled_tasks),
            "running_pipelines": len(self.scheduler.running_pipelines),
            "completed_pipelines": len(self.scheduler.completed_pipelines),
            "available_templates": list(TaskTemplate.list_templates())
        }
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {"name": name, **template}
            for name, template in TaskTemplate.TEMPLATES.items()
        ]


# CLI interface
if __name__ == "__main__":
    import argparse
    
    engine = TaskAutomationEngine()
    
    parser = argparse.ArgumentParser(description="Task Automation Engine")
    subparsers = parser.add_subparsers(dest="command")
    
    # Status
    subparsers.add_parser("status", help="Show engine status")
    
    # List templates
    templates_parser = subparsers.add_parser("templates", help="List templates")
    
    # Schedule
    schedule_parser = subparsers.add_parser("schedule", help="Schedule a task")
    schedule_parser.add_argument("--name", required=True)
    schedule_parser.add_argument("--template", required=True)
    schedule_parser.add_argument("--interval", type=int, help="Interval in seconds")
    schedule_parser.add_argument("--params", default="{}", help="JSON params")
    
    # Run due
    subparsers.add_parser("run-due", help="Run due tasks")
    
    # List tasks
    subparsers.add_parser("tasks", help="List scheduled tasks")
    
    args = parser.parse_args()
    
    if args.command == "status":
        status = engine.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "templates":
        for t in engine.list_templates():
            print(f"  • {t['name']}: {t['description']}")
    
    elif args.command == "schedule":
        params = json.loads(args.params)
        task_id = engine.schedule(args.name, args.template, params, args.interval)
        print(f"Scheduled task: {task_id}")
    
    elif args.command == "run-due":
        results = engine.run_due()
        print(f"Ran {len(results)} tasks")
        for r in results:
            print(f"  - {r['name']}: {r['result']['status']}")
    
    elif args.command == "tasks":
        for task in engine.scheduler.list_tasks():
            print(f"  • {task['name']} ({task['id']}) - {task['status']}")
            print(f"    Next run: {task['next_run']}")
    
    else:
        parser.print_help()