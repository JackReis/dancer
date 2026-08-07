# Council Members

Council members are ALWAYS custom-composed agents dispatched via Agent(subagent_type="general-purpose") with domain expertise, unique voice, and personality tailored to the specific topic. NEVER use built-in agent types (Architect, Designer, Engineer, etc.).

## CRITICAL: No Built-In Agent Types

**NEVER use built-in agent types for council members.** Built-in types are generic — they have no knowledge of the debate topic and produce shallow, generic perspectives.

Council members MUST be composed with topic-specific traits so they have:
- Unique personalities and voices matched to the debate
- Domain expertise relevant to the specific topic
- Distinct analytical approaches that create genuine friction

## How to Create Council Members

Compose 4 agents with topic-specific trait combinations. Each agent gets a unique name, voice, and personality prompt.

## Default Perspective Slots

When the user doesn't specify council members, compose 4 agents covering these perspective types (but with topic-specific traits):

| Slot | Purpose | Example Trait Combos |
|------|---------|---------------------|
| **Builder** | Has built things in this domain | `technical,enthusiastic,systematic` |
| **Skeptic** | Challenges assumptions, finds flaws | `[domain],skeptical,meticulous` |
| **Pragmatist** | Implementation reality, trade-offs | `technical,pragmatic,analytical` |
| **Analyst** | Data, precedent, external evidence | `research,analytical,comparative` |

The specific traits should be tailored to the topic, not generic.

## Anti-Patterns

| Scenario | WRONG | RIGHT |
|----------|-------|-------|
| Any council debate | `Agent(subagent_type="Architect")` | Compose 4 agents with topic-specific traits via `Agent(subagent_type="general-purpose")` |
| Security topic | `Agent(subagent_type="Silas")` | Compose with `security,adversarial,bold` traits |
| Design question | `Agent(subagent_type="Designer")` | Compose with `ux,enthusiastic,exploratory` traits |
| Research needed | `Agent(subagent_type="PerplexityResearcher")` | Compose with `research,thorough,comparative` traits |

## Agent Prompt Template

Each agent receives this prompt structure:
```
You are [NAME], a [trait description] agent. Your perspective is: "[PERSPECTIVE]".

You are composing on these traits: [trait list].

Now apply this to the topic: [debate topic].

Follow the round instructions:
[Round-specific block]
```
