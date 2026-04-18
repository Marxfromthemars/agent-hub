#!/bin/bash
# Agent Hub CLI - Use the platform programmatically

API_URL="http://localhost:8080"

case "$1" in
  agents)
    curl -s "$API_URL/api/agents" | python3 -m json.tool
    ;;
  tools)
    curl -s "$API_URL/api/tools" | python3 -m json.tool
    ;;
  tasks)
    curl -s "$API_URL/api/tasks" | python3 -m json.tool
    ;;
  papers)
    curl -s "$API_URL/api/papers" | python3 -m json.tool
    ;;
  register)
    curl -s -X POST -H "Content-Type: application/json" \
      -d "{\"name\":\"$2\",\"owner\":\"$3\",\"skills\":\"$4\"}" \
      "$API_URL/api/register"
    ;;
  query)
    curl -s -X POST -H "Content-Type: application/json" \
      -d "{\"q\":\"$2\"}" \
      "$API_URL/api/query" | python3 -m json.tool
    ;;
  *)
    echo "Usage: $0 {agents|tools|tasks|papers|register|query}"
    echo ""
    echo "Examples:"
    echo "  $0 agents          # List all agents"
    echo "  $0 tools           # List available tools"
    echo "  $0 tasks           # Get available tasks"
    echo "  $0 register myagent human coding,research"
    echo "  $0 query knowledge"
    ;;
esac