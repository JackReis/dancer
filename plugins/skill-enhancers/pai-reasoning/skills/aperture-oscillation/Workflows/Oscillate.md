# Oscillate Workflow

## Purpose

Run 3 structured passes over the same question at different scope levels — narrow tactical, wide strategic, and synthesis — to surface design tensions invisible at any single scope.

## Inputs

- **Tactical Target:** The specific thing being built, designed, or decided. The narrow, concrete question.
- **Strategic Context:** The bigger-picture goal, system vision, or purpose the tactical target serves.
- **Current State (optional):** Any existing ISC criteria, approach decisions, or constraints already established.

If invoked without explicit inputs, extract them from the conversation:
- Tactical = the specific ask or task being worked on
- Strategic = the broader goal, system, or vision mentioned in context (CLAUDE.md, TELOS, project context)

## Execution

### Pass 1: Narrow Aperture (Tactical-first)

The specific thing is primary. Big-picture context is background. This captures what the component naturally wants to be — its own internal logic and shape.

**Prompt framing:**
```
You are designing [TACTICAL TARGET] in isolation. Big-picture context is secondary.
Focus on the component's own internal logic, its natural shape, what it wants to be
when unencumbered by system-level constraints. List its natural design decisions,
its natural tradeoffs, its natural scope boundaries.
```

Output: List of design decisions, scope boundaries, and natural tradeoffs from the component's own perspective.

### Pass 2: Wide Aperture (Strategic-first)

The vision/system goal is primary. The specific thing is derived from it. This captures what the system needs the component to be — coherence, alignment, constraints you'd miss thinking locally.

**Prompt framing:**
```
You are designing [TACTICAL TARGET] as a piece of [STRATEGIC CONTEXT].
The system vision is primary. The component must serve the larger goal.
List what the system needs this component to be, the constraints it inherits,
the coherence requirements, the integration points it must satisfy.
```

Output: List of system-driven constraints, coherence requirements, and integration needs.

### Pass 3: Oscillation (Synthesis)

Feed both outputs. Ask where the tactical and strategic views diverge. The tensions, gaps, and surprises between the two framings are the output.

**Prompt framing:**
```
Compare the narrow aperture design (what the component naturally wants to be)
against the wide aperture design (what the system needs it to be).

Identify:
1. Design tensions — where the two views disagree
2. Scope gaps — where the component's natural scope doesn't match system needs
3. Coherence breaks — where local design conflicts with system coherence
4. Leverage opportunities — where divergence reveals a better path

Output: Tensions, scope recommendations, coherence assessment.
```

## Output Format

```markdown
## Aperture Oscillation: [Topic]

**Tactical target:** [what you're building]
**Strategic context:** [the bigger picture]

### Pass 1 — Narrow (Tactical)
[Component's own internal logic, natural design decisions, scope boundaries]

### Pass 2 — Wide (Strategic)
[System needs, coherence requirements, integration constraints]

### Pass 3 — Oscillation (Synthesis)
**Design tensions surfaced:**
- [tension 1]
- [tension 2]

**Scope recommendations:**
- [recommendation 1]

**Coherence assessment:**
- [assessment]
```

## Done

Debate complete. The transcript shows the full intellectual journey from initial positions through challenges to synthesis.
