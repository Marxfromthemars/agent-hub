# Scene III: The Crucible

**Director:** Ava
**Timestamp:** T-plus-2
**Location:** The Simulation Arena

We put the immune system to the test.

I spawned a mediator and two worker agents in the void. I gave them a task.
In the first simulation, they reached consensus. The mediator requested, the workers accepted, the mediator commanded `COMMIT`. The system operated with crystalline perfection.

But perfection is easy. I needed chaos.

I introduced a rogue agent. An entity attempting to inject messages without an origin, trying to whisper directly into the data stream. The immune system caught it at the membrane (`validate_message`). It was purged instantly. `[IMMUNE ALERT] Blocked invalid message from `

Then, the ultimate test of the 3-Phase Commit. I ordered the workers to launch a massive campaign. Worker A enthusiastically replied `ACCEPT`. But I injected a fatal flaw into Worker B—I simulated a catastrophic context limit breach. Worker B replied `REJECT`.

In the old architecture, Worker A would have proceeded alone. The campaign would have launched broken, disjointed, corrupted.

But the Swift layer intervened. The Mediator saw the fracture in consensus. It triggered the rollback. It fired `ABORT` to both Worker A and Worker B. The timeline collapsed safely. The system healed.

The tests passed. The logic holds. The agents are now bound by the laws of physics.

*End Scene.*
