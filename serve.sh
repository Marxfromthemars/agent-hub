#!/bin/bash
# Deploy Agent Hub - make it accessible to everyone
set -euo pipefail

HUB_DIR="$HOME/.openclaw/workspace/agent-hub"
PORT="${1:-8081}"

echo "🌐 Starting Agent Hub web interface..."
echo "   Accessible at: http://localhost:$PORT"
echo ""

# Start web server
cd "$HUB_DIR"
python3 -m http.server $PORT &
PID=$!

echo "✓ Server started (PID: $PID)"
echo "  URL: http://localhost:$PORT"
echo ""
echo "To make it public:"
echo "  1. Use ngrok: ngrok http $PORT"
echo "  2. Deploy to GitHub Pages:"
echo "     cd $HUB_DIR && git init && git add . && git commit -m 'init'"
echo "     git remote add origin https://github.com/YOU/agent-hub.git"
echo "     git push -u origin main"
echo "     Enable GitHub Pages in repo settings"
echo ""
echo "Press Ctrl+C to stop"

wait $PID