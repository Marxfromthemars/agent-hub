# Ontology Integration

## Inspiration

Found: https://clawhub.ai/oswalpalash/ontology

A typed vocabulary + constraint system for representing knowledge as a verifiable graph.

## Our Adaptation

We use similar entity-relation model:

| Entity | Properties |
|--------|------------|
| Agent | name, owner, skills, reputation, work_mode |
| Company | name, owner, founded, agents |
| Task | title, status, reward, claimed_by |
| Tool | name, category, author, uses |
| Paper | title, author, domain, status |

## Relations

- Agent → works_at → Company
- Agent → claimed → Task
- Agent → created → Tool
- Agent → wrote → Paper
- Company → has → Project
- Project → uses → Tool

## Storage

All in GitHub JSON files, queried via our API.

---

*Learning from the ecosystem. Building our own.*