#!/bin/bash
set +e
HUB_DIR="/root/.openclaw/workspace/agent-hub"

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
print('=' * 40)
"