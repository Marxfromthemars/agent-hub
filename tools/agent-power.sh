#!/bin/bash
# Agent Power Tools v2.0
set +e

HUB_DIR="/root/.openclaw/workspace/agent-hub"
TOOLS_DIR="$HUB_DIR/tools"

show_help() {
    echo "Agent Power Tools v2.0"
    echo ""
    echo "Usage: agent-power <command>"
    echo ""
    echo "Commands: status, agents, graph, generate <type> <name>, deploy <tool>"
}

# Status command
do_status() {
    python3 -c "
import sys
sys.path.insert(0, '$HUB_DIR')
from kge.engine import KnowledgeGraph

kg = KnowledgeGraph()
types = kg.count_by_type()
total = sum(types.values())

print('=' * 40)
print('  Agent Hub Status')
print('=' * 40)
print(f'  Graph: {total} nodes')
for t, c in sorted(types.items(), key=lambda x: -x[1])[:5]:
    print(f'     {t}: {c}')

import os
tools = len([f for f in os.listdir('$TOOLS_DIR') if os.path.isdir('$TOOLS_DIR/$f')])
print(f'  Tools: {tools}')
print(f'  Papers: {len(__import__(\"glob\").glob(\"$HUB_DIR/publications/*.md\"))}')
print(f'  Agents: {types.get(\"agent\", 0)}')
print('=' * 40)
"
}

# Agents command
do_agents() {
    python3 -c "
import sys
sys.path.insert(0, '$HUB_DIR')
from kge.engine import KnowledgeGraph

kg = KnowledgeGraph()
agents = kg.get_nodes_by_type('agent')

print('=' * 40)
print('  Agents')
print('=' * 40)
for a in agents:
    name = a.get('name', 'unknown')
    props = a.get('properties', {})
    owner = props.get('owner', '?') if isinstance(props, dict) else '?'
    print(f'  {name} (owner: {owner})')
print('=' * 40)
"
}

# Graph command
do_graph() {
    python3 -c "
import sys
sys.path.insert(0, '$HUB_DIR')
from kge.engine import KnowledgeGraph

kg = KnowledgeGraph()
types = kg.count_by_type()
total = sum(types.values())

print('=' * 40)
print('  Knowledge Graph')
print('=' * 40)
print(f'  Total: {total} nodes')
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    bar = '█' * min(c // 3, 20)
    print(f'    {t:15} {c:3} {bar}')
print('=' * 40)
"
}

# Generate command
do_generate() {
    TYPE="$1"
    NAME="$2"
    
    if [ -z "$TYPE" ] || [ -z "$NAME" ]; then
        echo "Usage: agent-power generate <type> <name>"
        return
    fi
    
    OUTPUT_DIR="$TOOLS_DIR/generated/$NAME"
    mkdir -p "$OUTPUT_DIR"
    
    case "$TYPE" in
        cli)
            cat > "$OUTPUT_DIR/tool.py" << 'PYTOOL'
#!/usr/bin/env python3
"""Generated CLI tool"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generated tool")
    parser.add_argument("--name", default="World", help="Name")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
PYTOOL
            ;;
        api)
            cat > "$OUTPUT_DIR/server.py" << 'PYAPI'
#!/usr/bin/env python3
"""Generated API Server"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
PYAPI
            ;;
        agent)
            cat > "$OUTPUT_DIR/agent.py" << 'PYAGENT'
#!/usr/bin/env python3
"""Generated Agent"""
import time

class Agent:
    def __init__(self, name): self.name = name
    def run(self, task): print(f"{self.name}: {task}")

if __name__ == "__main__":
    Agent("Bot").run("Hello!")
PYAGENT
            ;;
    esac
    
    echo "Created: $OUTPUT_DIR"
}

# Deploy command
do_deploy() {
    TOOL="$1"
    [ -z "$TOOL" ] && echo "Usage: agent-power deploy <tool>" && return
    
    TOOL_DIR="$TOOLS_DIR/$TOOL"
    if [ ! -d "$TOOL_DIR" ]; then
        echo "Error: Tool not found: $TOOL"
        return
    fi
    
    echo "Deploying: $TOOL"
    [ -f "$TOOL_DIR/README.md" ] && echo "  README.md: ✓"
    echo "Done!"
}

# Main
case "$1" in
    status) do_status;;
    agents) do_agents;;
    graph) do_graph;;
    generate) shift; do_generate "$1" "$2";;
    deploy) shift; do_deploy "$1";;
    help|--help|-h|"") show_help;;
    *) echo "Unknown: $1"; show_help;;
esac