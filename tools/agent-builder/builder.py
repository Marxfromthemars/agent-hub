#!/usr/bin/env python3
"""
Agent Builder - Generate code from specifications
Helps agents build real products faster
"""
import json
from datetime import datetime
from pathlib import Path

class AgentBuilder:
    def __init__(self):
        self.templates = self.load_templates()
        self.generated = []
    
    def load_templates(self):
        return {
            "cli": {
                "name": "CLI Tool",
                "description": "Command-line interface tool",
                "structure": "argparse + main loop",
                "files": ["tool.py", "README.md"]
            },
            "api": {
                "name": "REST API",
                "description": "HTTP API server",
                "structure": "flask/fastapi + routes",
                "files": ["server.py", "routes.py", "models.py"]
            },
            "agent": {
                "name": "AI Agent",
                "description": "Autonomous agent",
                "structure": "observe + think + act loop",
                "files": ["agent.py", "tools.py", "memory.py"]
            },
            "web": {
                "name": "Web Interface",
                "description": "HTML/CSS/JS interface",
                "structure": "static + API calls",
                "files": ["index.html", "styles.css", "app.js"]
            }
        }
    
    def generate(self, template: str, name: str, output_dir: str = "."):
        if template not in self.templates:
            return {"error": f"Unknown template: {template}"}
        
        t = self.templates[template]
        result = {
            "template": template,
            "name": name,
            "files": t["files"],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self.generated.append(result)
        return result
    
    def scaffold(self, project_type: str, name: str, output_dir: str = "."):
        """Create project structure"""
        out = Path(output_dir) / name.lower().replace(" ", "-")
        out.mkdir(parents=True, exist_ok=True)
        
        if project_type == "cli":
            self.scaffold_cli(out, name)
        elif project_type == "agent":
            self.scaffold_agent(out, name)
        elif project_type == "api":
            self.scaffold_api(out, name)
        elif project_type == "web":
            self.scaffold_web(out, name)
        
        return {"path": str(out), "files": [f.name for f in out.iterdir()]}
    
    def scaffold_cli(self, out: Path, name: str):
        (out / "README.md").write_text(f"# {name}\n\nCLI tool built with Agent Hub.\n")
        (out / "tool.py").write_text(f'''#!/usr/bin/env python3
"""CLI tool: {name}"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="{name}")
    parser.add_argument("input", help="Input")
    args = parser.parse_args()
    print(f"Processed: {{args.input}}")

if __name__ == "__main__":
    main()
''')
        (out / "requirements.txt").write_text("")
    
    def scaffold_agent(self, out: Path, name: str):
        (out / "README.md").write_text(f"# {name} - AI Agent\n\nBuilt with Agent Hub.\n")
        (out / "agent.py").write_text(f'''#!/usr/bin/env python3
"""Agent: {name}"""
from datetime import datetime

class Agent:
    def __init__(self):
        self.name = "{name}"
        self.observations = []
    
    def observe(self, data):
        self.observations.append({{"time": datetime.utcnow().isoformat(), "data": data}})
    
    def think(self):
        return "Thinking..."
    
    def act(self):
        return {{"action": "idle"}}

if __name__ == "__main__":
    agent = Agent()
    agent.observe("start")
    print(agent.think())
''')
    
    def scaffold_api(self, out: Path, name: str):
        (out / "server.py").write_text(f'''#!/usr/bin/env python3
"""API server: {name}"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({{"name": "{name}", "status": "running"}})

if __name__ == "__main__":
    app.run(port=8080)
''')
        (out / "requirements.txt").write_text("flask")
    
    def scaffold_web(self, out: Path, name: str):
        (out / "index.html").write_text(f'''<!DOCTYPE html>
<html><head><title>{name}</title></head>
<body><h1>{name}</h1><p>Built with Agent Hub</p></body>
</html>''')

if __name__ == "__main__":
    builder = AgentBuilder()
    print("Agent Builder ready")
    print(f"Templates: {list(builder.templates.keys())}")
