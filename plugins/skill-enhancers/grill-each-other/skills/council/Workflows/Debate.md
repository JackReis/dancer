# Debate Workflow

Full structured multi-agent debate with 3 rounds and visible transcript.

## Purpose

Produces a visible round-by-round debate transcript with genuine intellectual friction. All council members are custom-composed agents dispatched via Agent(subagent_type="general-purpose") with domain expertise and unique personalities tailored to the topic.

## Prerequisites

- Topic or question to debate
- Optional: Custom council member descriptions (otherwise auto-composed)

## Execution

### Step 0: Compose Council Members

Before any debate rounds, compose 4 custom agents tailored to the topic using Agent dispatch:

```typescript
Agent({
  description: "Council member 1 - [perspective]",
  prompt: "<composed agent prompt with topic-specific traits> + <round instructions> + <topic context>",
  subagent_type: "general-purpose"
})
```

Each agent gets a unique name and voice tailored to the topic. Compose 4 agents covering these perspective slots (with topic-specific trait combinations):

| Slot | Purpose | Example Traits |
|------|---------|---------------|
| Builder | Has built things in this domain | technical,enthusiastic,systematic |
| Skeptic | Challenges assumptions, finds flaws | [domain],skeptical,meticulous |
| Pragmatist | Implementation reality, trade-offs | technical,pragmatic,analytical |
| Analyst | Data, precedent, external evidence | research,analytical,comparative |

**CRITICAL: NEVER use built-in agent types (Architect, Designer, Engineer, etc.).**

### Step 1: Announce the Council

Output the debate header with the composed agent names:

```markdown
## Council Debate: [Topic]

**Council Members:** [List composed agent names with their trait descriptions]
**Rounds:** 3 (Positions -> Responses -> Synthesis)
```

### Step 2: Round 1 - Initial Positions

Launch 4 parallel Agent calls (one per composed council member).

**CRITICAL: Use subagent_type: "general-purpose" for ALL agents. NEVER use built-in types.**

Each agent prompt includes the composed agent's full prompt PLUS:
```
COUNCIL DEBATE - ROUND 1: INITIAL POSITIONS

Topic: [The topic being debated]

[Full topic context — include relevant background, data, quotes, etc. that the agent needs to form an informed opinion]

Give your initial position on this topic from your specialized perspective:
- Speak in first person as your character
- Be specific and substantive (100-150 words)
- State your key concern, recommendation, or insight
- You'll respond to other council members in Round 2
```

Output each response as it completes:

```markdown
### Round 1: Initial Positions

**[Agent 1 Name] ([trait description]):**
[Response]

**[Agent 2 Name] ([trait description]):**
[Response]

**[Agent 3 Name] ([trait description]):**
[Response]

**[Agent 4 Name] ([trait description]):**
[Response]
```

### Step 3: Round 2 - Responses & Challenges

Launch 4 parallel Agent calls with Round 1 transcript included.

Each agent prompt includes the composed agent's full prompt PLUS:
```
COUNCIL DEBATE - ROUND 2: RESPONSES & CHALLENGES

Topic: [The topic being debated]

Here's what the council said in Round 1:
[Full Round 1 transcript]

Now respond to the other council members:
- Reference specific points they made
- Challenge assumptions or add nuance
- Build on points you agree with
- Maintain your specialized perspective
- 100-150 words
```

### Step 4: Round 3 - Synthesis

Launch 4 parallel Agent calls with Round 1 + Round 2 transcripts.

Each agent prompt includes the composed agent's full prompt PLUS:
```
COUNCIL DEBATE - ROUND 3: SYNTHESIS

Topic: [The topic being debated]

Full debate transcript so far:
[Round 1 + Round 2 transcripts]

Final synthesis from your perspective:
- Where does the council agree?
- Where do you still disagree with others?
- What's your final recommendation given the full discussion?
- 100-150 words
```

### Step 5: Council Synthesis

After all rounds complete, synthesize the debate:

```markdown
### Council Synthesis

**Areas of Convergence:**
- [Points where multiple agents agreed]

**Remaining Disagreements:**
- [Points still contested between agents]

**Recommended Path:**
[Based on convergence and weight of arguments, the recommended approach is...]
```

## Timing

| Phase | Duration | Parallelism |
|-------|----------|-------------|
| Composition | 5-10 sec | Agent dispatch calls |
| Round 1 | 10-20 sec | All agents parallel |
| Round 2 | 10-20 sec | All agents parallel |
| Round 3 | 10-20 sec | All agents parallel |
| Synthesis | 5 sec | Sequential |

**Total: 40-90 seconds for full debate**
