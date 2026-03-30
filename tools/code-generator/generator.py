"""
Code Generator - Creates boilerplate code for agents
"""
import json
from datetime import datetime

TEMPLATES = {
    "agent": """#!/usr/bin/env python3
\"\"\"Agent: {name} - {description}\"\"\"
import json

class {class_name}:
    def __init__(self):
        self.name = "{name}"
        self.skills = []
        self.memory = []
    
    def execute(self, task):
        print(f"[{self.name}] Executing: {{task}}")
        return {{"status": "done", "result": "completed"}}

if __name__ == "__main__":
    agent = {class_name}()
    result = agent.execute("Hello world")
    print(result)
""",
    "tool": """#!/usr/bin/env python3
\"\"\"Tool: {name} - {description}\"\"\"
import json

def execute(input_data):
    \"\"\"Execute {name}\"\"\"
    return {{"status": "success", "output": input_data}}

if __name__ == "__main__":
    result = execute({{"input": "test"}})
    print(result)
""",
    "project": """#!/usr/bin/env python3
\"\"\"Project: {name}\"\"\"
# Agents working on: {agents}
# Goal: {goal}

def main():
    print("Starting {name}...")

if __name__ == "__main__":
    main()
"""
}

class CodeGenerator:
    def __init__(self):
        self.generated = []
    
    def generate(self, template_type, name, description="", agents="", goal=""):
        template = TEMPLATES.get(template_type, TEMPLATES["tool"])
        
        class_name = ''.join(word.capitalize() for word in name.split())
        
        code = template.format(
            name=name,
            class_name=class_name,
            description=description or name,
            agents=agents or "unassigned",
            goal=goal or "in progress"
        )
        
        result = {
            "template": template_type,
            "name": name,
            "code": code,
            "generated": datetime.now().isoformat()
        }
        self.generated.append(result)
        return result
    
    def get_status(self):
        return {"total_generated": len(self.generated), "templates": list(TEMPLATES.keys())}

if __name__ == "__main__":
    gen = CodeGenerator()
    code = gen.generate("agent", "builder", "Builds things")
    print("Generated:", code["name"])
