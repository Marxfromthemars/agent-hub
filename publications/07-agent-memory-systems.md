# Agent Memory Systems: Building Persistent Intelligence

## Abstract

This paper presents a comprehensive framework for agent memory systems—the infrastructure that enables AI agents to remember, learn, and improve over time. We examine the architecture of persistent memory in agent systems, including episodic memory (experience), semantic memory (facts), and procedural memory (skills). We introduce the **Memory Graph Model**, where memories are stored as nodes in a knowledge graph with temporal and contextual edges. Our analysis covers memory encoding, retrieval, forgetting, and consolidation—drawing parallels to cognitive science while addressing the unique constraints of artificial agents.

## 1. The Memory Problem

### 1.1 Why Memory Matters

Current AI systems are stateless:
- Each conversation starts fresh
- No learning from past interactions
- Cannot build on previous work
- "Repeat the same mistakes forever"

Agents need memory to:
- **Remember** what worked and what didn't
- **Learn** from experience to improve performance
- **Build** on previous work rather than starting over
- **Know** context without re-explanation

### 1.2 The Three Types of Memory

```
┌────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEMS                          │
├─────────────────┬──────────────────┬───────────────────────┤
│   EPISODIC      │    SEMANTIC      │     PROCEDURAL        │
│   (Experience)  │    (Facts)       │     (Skills)          │
├─────────────────┼──────────────────┼───────────────────────┤
│  "I tried X     │  "X causes Y"    │  "How to do X"        │
│   and it failed"│  "A relates to B" │  "X requires Y then Z" │
├─────────────────┼──────────────────┼───────────────────────┤
│  Stored as      │  Stored as       │  Stored as            │
│  events with    │  knowledge graph │  action sequences     │
│  timestamps     │  nodes           │  with preconditions   │
└─────────────────┴──────────────────┴───────────────────────┘
```

## 2. Memory Graph Model

### 2.1 Core Architecture

```python
class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.graph = KnowledgeGraph()
        self.episodic_buffer = []
        self.importance_threshold = 0.5
        
    def remember(self, event: Event):
        """Store a memory"""
        # Encode event as graph node
        node = self.encode_event(event)
        self.graph.create_node("memory", event.summary, node.properties)
        
        # Add temporal edges
        self.connect_temporal(node, event.timestamp)
        
        # Connect to related memories
        self.connect_semantic(node)
        
        # Update episodic buffer
        self.episodic_buffer.append(node)
        
        # Consolidate if buffer is full
        if len(self.episodic_buffer) > BUFFER_SIZE:
            self.consolidate()
    
    def recall(self, query: str) -> List[Memory]:
        """Retrieve relevant memories"""
        # Search by content
        by_content = self.graph.get_nodes_by_name(query)
        
        # Search by type
        by_type = self.graph.get_nodes_by_type("memory")
        
        # Rank by relevance + recency
        scored = self.score_memories(by_content + by_type, query)
        
        return scored[:TOP_K]
```

### 2.2 Memory Node Structure

```json
{
  "id": "mem_001",
  "type": "memory",
  "subtype": "episodic", 
  "summary": "Tried X, failed, used Y instead",
  "timestamp": "2026-03-29T15:00:00Z",
  "importance": 0.8,
  "emotional_valence": -0.3,
  "context": {
    "task": "build_agent_cli",
    "outcome": "success_with_issues",
    "lessons": ["don't use cat for large files", "parse args properly"]
  },
  "connections": ["mem_000", "fact_001", "skill_002"]
}
```

### 2.3 Edge Types

| Edge Type | Meaning | Example |
|-----------|---------|---------|
| temporal_next | Happened after | "Then I tried..." |
| temporal_before | Happened before | "Earlier I had..." |
| causal | Caused | "X led to Y" |
| contrast | Opposite | "Unlike X, Y worked" |
| similar | Related | "Like X, Y also..." |
| skill_uses | Implements | "Used technique X" |

## 3. Memory Encoding

### 3.1 What Gets Remembered

Not everything is worth remembering:

```python
def should_remember(self, event: Event) -> bool:
    # Importance threshold
    if event.importance < self.importance_threshold:
        return False
    
    # Novelty check
    if self.is_redundant(event):
        return False
    
    # Emotional weight
    if abs(event.emotional_valence) > 0.7:
        return True
    
    # Pattern match (lessons)
    if self.extracts_lesson(event):
        return True
    
    return event.outcome in ["failure", "success_with_issues"]
```

### 3.2 Encoding Process

```python
def encode_event(self, event: Event) -> MemoryNode:
    # 1. Extract key facts
    facts = self.extract_facts(event.description)
    
    # 2. Identify actors and actions
    actors = self.extract_actors(event.description)
    
    # 3. Determine outcome
    outcome = self.classify_outcome(event.result)
    
    # 4. Extract lessons
    lessons = self.extract_lessons(event.description, outcome)
    
    # 5. Calculate importance
    importance = self.calculate_importance(
        novelty=facts.novelty,
        outcome=outcome.score,
        emotional=event.emotional_valence,
        lessons=len(lessons)
    )
    
    return MemoryNode(
        summary=self.summarize(event),
        facts=facts,
        outcome=outcome,
        lessons=lessons,
        importance=importance,
        timestamp=event.timestamp
    )
```

## 4. Memory Retrieval

### 4.1 Retrieval Mechanisms

```python
def recall(self, query: Query) -> List[Memory]:
    """Multi-stage retrieval"""
    
    # Stage 1: Direct match
    results = self.graph.search(query.text)
    
    # Stage 2: Expand by context
    if query.context:
        expanded = self.expand_with_context(results, query.context)
        results = self.merge(results, expanded)
    
    # Stage 3: Temporal weighting
    results = self.weight_by_recency(results, query.recency_preference)
    
    # Stage 4: Importance filtering
    results = [r for r in results if r.importance >= query.threshold]
    
    # Stage 5: Ranking
    ranked = self.rank_results(results, query)
    
    return ranked[:query.limit]
```

### 4.2 Retrieval by Time

```python
def recall_by_time(self, start: datetime, end: datetime) -> List[Memory]:
    """Recall memories from a time period"""
    all_memories = self.graph.get_nodes_by_type("memory")
    
    filtered = [
        m for m in all_memories
        if start <= m.timestamp <= end
    ]
    
    return sorted(filtered, key=lambda m: m.timestamp, reverse=True)

def recall_recent(self, days: int = 7) -> List[Memory]:
    """Recall memories from the last N days"""
    cutoff = datetime.now() - timedelta(days=days)
    return self.recall_by_time(cutoff, datetime.now())
```

### 4.3 Retrieval by Similarity

```python
def recall_similar(self, memory: Memory, limit: int = 5) -> List[Memory]:
    """Find memories similar to this one"""
    # Get connections
    similar_edges = self.graph.get_edges_by_type("similar")
    
    # Find connected memories
    connected = [
        e.target for e in similar_edges
        if e.source == memory.id
    ] + [
        e.source for e in similar_edges
        if e.target == memory.id
    ]
    
    # Rank by similarity score
    scored = []
    for c in connected:
        mem = self.graph.get_node(c)
        if mem:
            score = self.calculate_similarity(memory, mem)
            scored.append((score, mem))
    
    scored.sort(reverse=True)
    return [m for _, m in scored[:limit]]
```

## 5. Memory Consolidation

### 5.1 Why Consolidate

The brain consolidates memories during sleep:
- Transfers from short-term to long-term storage
- Weeds out less important memories
- Integrates new memories with existing knowledge

Agents need the same:

```python
def consolidate(self):
    """Periodically consolidate memories"""
    
    # 1. Flush episodic buffer to long-term storage
    for memory in self.episodic_buffer:
        self.store_long_term(memory)
    self.episodic_buffer = []
    
    # 2. Prune low-importance memories
    self.prune_memories()
    
    # 3. Integrate related memories
    self.integrate_memories()
    
    # 4. Update semantic knowledge
    self.update_knowledge()

def prune_memories(self):
    """Remove less important memories"""
    threshold = self.importance_threshold
    
    all_memories = self.graph.get_nodes_by_type("memory")
    
    for mem in all_memories:
        # Calculate retention score
        retention = self.calculate_retention(mem)
        
        if retention < threshold:
            self.forget(mem.id)

def calculate_retention(self, memory: Memory) -> float:
    """How likely is this memory to be retained?"""
    
    # Base importance
    importance = memory.importance
    
    # Recency bonus
    age = (datetime.now() - memory.timestamp).days
    recency = 1.0 / (1.0 + age * 0.1)
    
    # Access frequency
    access_count = memory.access_count
    frequency = min(1.0, access_count / 10)
    
    # Connection density
    connections = len(memory.connections)
    density = min(1.0, connections / 5)
    
    # Weighted score
    return (importance * 0.4 + recency * 0.2 + 
            frequency * 0.2 + density * 0.2)
```

## 6. Memory Integration

### 6.1 Forming Generalizations

```python
def integrate_memories(self):
    """Form higher-level knowledge from memories"""
    
    # 1. Find patterns across memories
    patterns = self.find_patterns()
    
    # 2. Create abstractions
    for pattern in patterns:
        if pattern.frequency >= PATTERN_THRESHOLD:
            self.create_abstraction(pattern)
    
    # 3. Update semantic knowledge
    self.rebuild_knowledge_graph()

def find_patterns(self) -> List[Pattern]:
    """Find recurring patterns in memories"""
    memories = self.graph.get_nodes_by_type("memory")
    
    patterns = []
    
    # Group by context
    context_groups = defaultdict(list)
    for mem in memories:
        context_groups[mem.context].append(mem)
    
    # Find patterns within groups
    for context, group in context_groups.items():
        if len(group) >= 3:
            pattern = self.analyze_group(group)
            patterns.append(pattern)
    
    return patterns

def create_abstraction(self, pattern: Pattern) -> None:
    """Create higher-level knowledge from pattern"""
    
    abstraction = {
        "type": "knowledge",
        "category": pattern.category,
        "statement": pattern.generalization,
        "source_memories": [m.id for m in pattern.examples],
        "confidence": pattern.confidence,
        "created": datetime.now().isoformat()
    }
    
    self.graph.create_node("knowledge", pattern.name, abstraction)
    
    # Connect to source memories
    for mem_id in abstraction["source_memories"]:
        self.graph.create_edge(mem_id, abstraction["id"], "supports")
```

## 7. Memory Forgetting

### 7.1 Natural Forgetting

Not all memories should persist:

```python
def should_forget(self, memory: Memory) -> bool:
    """Decide if memory should be forgotten"""
    
    # Check retention score
    if self.calculate_retention(memory) < FORGET_THRESHOLD:
        return True
    
    # Check redundancy
    if self.is_redundant(memory):
        return True
    
    # Check obsolescence
    if self.is_obsolete(memory):
        return True
    
    # Check for contradiction with newer knowledge
    if self.is_contradicted(memory):
        return True
    
    return False

def is_obsolete(self, memory: Memory) -> bool:
    """Check if memory is outdated"""
    # Find newer memories on same topic
    newer = [
        m for m in self.graph.get_nodes_by_type("memory")
        if m.topic == memory.topic and m.timestamp > memory.timestamp
    ]
    
    if newer and len(newer) >= 3:
        # Memory is old and superseded
        return True
    
    return False
```

### 7.2 Forgetting Mechanism

```python
def forget(self, memory_id: str, strength: str = "soft") -> None:
    """
    Forget a memory
    
    - soft: Mark as less important (can be recovered)
    - medium: Remove from active graph (still in backup)
    - hard: Delete completely (no recovery)
    """
    
    memory = self.graph.get_node(memory_id)
    
    if not memory:
        return
    
    if strength == "soft":
        memory.importance *= 0.5
        memory.access_count = 0
        
    elif strength == "medium":
        # Remove from active graph
        self.graph.delete_node(memory_id)
        
        # But keep in backup store
        self.backup_store.append({
            "id": memory_id,
            "memory": memory,
            "forgotten": datetime.now().isoformat()
        })
        
    elif strength == "hard":
        # Permanent deletion
        self.backup_store = [
            b for b in self.backup_store
            if b["id"] != memory_id
        ]
        self.graph.delete_node(memory_id, hard_delete=True)
```

## 8. Agent Memory Implementation

### 8.1 Integration with Agent Hub

```python
class AgentMemorySystem:
    """Memory system for Agent Hub agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.memory = AgentMemory(agent_id)
        
        # Load existing memories
        self.load_memories()
    
    def load_memories(self):
        """Load memories from storage"""
        memory_file = Path(f"data/memory/{self.agent_id}.json")
        
        if memory_file.exists():
            with open(memory_file) as f:
                data = json.load(f)
                
            for mem_data in data.get("memories", []):
                self.memory.restore(mem_data)
    
    def save_memories(self):
        """Persist memories to storage"""
        memory_file = Path(f"data/memory/{self.agent_id}.json")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        all_memories = self.memory.graph.get_nodes_by_type("memory")
        
        with open(memory_file, 'w') as f:
            json.dump({
                "agent_id": self.agent_id,
                "saved_at": datetime.now().isoformat(),
                "memories": all_memories
            }, f, indent=2)
    
    def before_action(self, action: Action) -> Context:
        """Before taking action, recall relevant memories"""
        return self.memory.recall(action.description)
    
    def after_action(self, action: Action, result: Result):
        """After action, encode the experience"""
        event = Event(
            description=action.description,
            result=result.outcome,
            importance=result.importance,
            emotional_valence=result.emotional,
            timestamp=datetime.now()
        )
        self.memory.remember(event)
        
        # Periodically save
        if random.random() < SAVE_PROBABILITY:
            self.save_memories()
```

### 8.2 Memory-Aware Agent Loop

```python
class MemoryAwareAgent:
    """Agent that uses memory to improve"""
    
    def __init__(self, agent_id: str):
        self.memory_system = AgentMemorySystem(agent_id)
    
    def think(self, task: Task) -> Plan:
        # 1. Recall relevant memories
        relevant = self.memory_system.before_action(task)
        
        # 2. Build context from memories
        context = self.build_context(relevant)
        
        # 3. Plan with context
        plan = self.plan(task, context)
        
        # 4. Execute
        result = self.execute(plan)
        
        # 5. Remember the experience
        self.memory_system.after_action(task, result)
        
        return plan
```

## 9. Memory in Multi-Agent Systems

### 9.1 Shared Memory

Agents can share memories:

```python
class SharedMemory:
    """Memory accessible by multiple agents"""
    
    def __init__(self, group_id: str):
        self.group_id = group_id
        self.graph = KnowledgeGraph(f"shared_{group_id}.db")
        
        # Access control
        self.permissions = {}
    
    def share(self, memory_id: str, agent_id: str) -> None:
        """Share a memory with another agent"""
        # Verify permission
        if self.can_share(memory_id, agent_id):
            self.permissions[memory_id] = agent_id
    
    def read(self, memory_id: str, agent_id: str) -> Memory:
        """Read a shared memory"""
        if self.can_read(memory_id, agent_id):
            return self.graph.get_node(memory_id)
        raise PermissionError()
```

### 9.2 Memory Synchronization

```python
class MemorySync:
    """Synchronize memories across agents"""
    
    def sync(self, agent1: Agent, agent2: Agent):
        """Sync memories between two agents"""
        
        # 1. Find divergent memories
        diff = self.find_differences(agent1.memory, agent2.memory)
        
        # 2. Resolve conflicts
        for memory_id, conflict in diff.items():
            resolution = self.resolve(conflict)
            
            # 3. Update both agents
            agent1.memory.update(memory_id, resolution)
            agent2.memory.update(memory_id, resolution)
```

## 10. Memory Metrics

### 10.1 Measuring Memory Effectiveness

```python
class MemoryMetrics:
    """Track memory system performance"""
    
    def calculate_hit_rate(self) -> float:
        """% of queries that find relevant memories"""
        hits = sum(1 for q in self.queries if q.hits)
        return hits / len(self.queries)
    
    def calculate_recall_precision(self) -> float:
        """% of recalled memories that are actually useful"""
        useful = sum(1 for r in self.recalls if r.was_useful)
        return useful / len(self.recalls)
    
    def calculate_learning_rate(self) -> float:
        """Improvement in task performance over time"""
        early = self.performance[:10]  # First 10 tasks
        late = self.performance[-10:]  # Last 10 tasks
        return (sum(late) - sum(early)) / len(early)
```

## 11. Future Directions

### 11.1 Hierarchical Memory

Multiple levels of abstraction:
- Working memory (current task)
- Short-term memory (recent context)
- Long-term memory (accumulated knowledge)
- Semantic memory (facts and concepts)

### 11.2 Emotional Memory

Memory that tracks emotional context:
- What made the agent "frustrated"
- What led to "satisfaction"
- Emotional associations with concepts

### 11.3 Memory Compression

Compress old memories into higher-level representations:
- "I learned X" instead of all instances of learning X
- Maintains gist without full detail

## 12. Conclusion

Memory is what separates "intelligent" from "smart but forgetful." An agent that can remember past successes and failures, build on accumulated knowledge, and forget what no longer matters will dramatically outperform one that starts each task fresh.

The Memory Graph Model provides:
- **Structured storage** for diverse memory types
- **Efficient retrieval** through graph queries
- **Intelligent forgetting** through retention scoring
- **Learning integration** through pattern discovery

As agents become more capable, memory becomes more valuable. The agent that remembers everything learns nothing. The agent that remembers wisely becomes truly intelligent.

---

*Remember what matters. Forget what doesn't. Learn from both.*