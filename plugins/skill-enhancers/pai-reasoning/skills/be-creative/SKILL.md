---
name: be-creative
description: Divergent ideation and corpus expansion using Verbalized Sampling + extended thinking. Single-shot mode generates 5 internally diverse candidates (p<0.10 each) and surfaces the strongest. Multi-turn mode expands a small seed corpus (5-20 examples) into a diverse N-example dataset for evals, training, or test sets. Research-backed: Zhang et al. 2025 — 1.6-2.1x diversity increase on creative writing, 25.7% quality improvement, synthetic-data downstream accuracy lift 30.6% to 37.5%. Seven workflows: StandardCreativity, MaximumCreativity, IdeaGeneration, TreeOfThoughts, DomainSpecific, TechnicalCreativity for algorithmic/architecture work, and SyntheticDataExpansion for corpus growth. NOT FOR multi-cycle evolutionary ideation with Lamarckian meta-learning (use ideate for that). NOT FOR factually-constrained tasks with one right answer. USE WHEN be creative, think outside the box, brainstorm, divergent ideas, creative solutions, maximum creativity, tree of thoughts, radically different, most creative option, creative angle, unconventional approach, name this, creative framing, narrative angle, artistic direction, expand this corpus, synthetic data, generate diverse examples, expand seed set, create test set from these examples.
---

# BeCreative

Enhance AI creativity using deep thinking + Verbalized Sampling. Combines research-backed techniques for 1.6-2.1x diversity increase and extended thinking for quality.

## Workflow Routing

| Workflow | Triggers | Description |
|----------|----------|-------------|
| StandardCreativity | "be creative", "think creatively", default creative tasks | Standard deep thinking + VS for quality creative work |
| MaximumCreativity | "maximum creativity", "most creative", "radically different" | Push boundaries, avoid all cliches, unconventional |
| IdeaGeneration | "brainstorm", "ideas for", "solve this problem" | Problem-solving and innovation focus |
| TreeOfThoughts | "complex problem", "multi-factor", "explore paths" | Branching exploration for complex challenges |
| DomainSpecific | "artistic", "business innovation", domain-specific | Domain-tailored creativity templates |
| TechnicalCreativity | "technical creativity", "algorithm", "architecture" | Engineering creativity |
| SyntheticDataExpansion | "expand corpus", "synthetic data", "generate diverse examples", "expand seed set", "create test set from these examples" | Multi-turn VS to grow a small seed corpus into a diverse N-example dataset |

## Quick Reference

**Core technique:** Generate 5 diverse options (p<0.10 each) internally, output single best response.

**Default approach:** For most creative requests, apply StandardCreativity workflow.

**For artistic/narrative creativity:** Apply workflow directly (no delegation needed).

**For technical creativity:** Use TechnicalCreativity workflow.

## Resource Index

| Resource | Description |
|----------|-------------|
| ResearchFoundation.md | Research backing, why it works, activation triggers |
| Principles.md | Core philosophy and best practices |
| Templates.md | Quick reference templates for all modes |
| Examples.md | Practical examples with expected outputs |

## Integration with Other Skills

**Works well with:**
- XPost / LinkedInPost - Generate creative social media content
- Blogging - Creative blog post ideas and narrative approaches
- Development - Creative technical solutions
- Art - Diverse image prompt ideas and creative directions
- Business - Creative offer frameworks and business models
- Research - Creative research angles and synthesis approaches
- Evals - Consume expanded corpora

## Decision: BeCreative vs Ideate

BeCreative and Ideate are kept as **separate skills** (not merged):

| Dimension | BeCreative | Ideate |
|-----------|-----------|--------|
| **Mode** | Single-shot, one response | Multi-cycle evolutionary system |
| **Process** | Verbalized Sampling (5 candidates, pick best) | 9 phases, Loop Controller, fitness scoring, meta-learning |
| **Output** | One best response | Ranked candidate list with provenance |
| **Use case** | "Be creative — name this", "creative angle on..." | "Novel ideas for X through evolution" |
| **When to use** | Fast divergent, output-focused | Deep evolutionary, process-focused |

This mirrors the source skill's own framing: "This is NOT Ideate — Ideate is an evolutionary system."

## Gotchas

- **This is for QUICK divergent brainstorming.** For deep multi-cycle evolutionary ideation, use ideate instead.
- **Verbalized Sampling requires extended thinking to work.** Ensure extended thinking is enabled when using this skill.
- **Diversity claims come from specific benchmark conditions.** Real-world diversity improvement varies with prompt type.
- **Not for factually-constrained tasks with one right answer.** VS provides no lift where there's a single correct answer.

## Examples

**Example 1: Creative blog angle**
```
User: "think outside the box for this AI ethics post"
-> Applies StandardCreativity workflow
-> Generates 5 diverse angles internally
-> Returns most innovative framing approach
```

**Example 2: Product naming brainstorm**
```
User: "be creative - need names for this security tool"
-> Applies MaximumCreativity workflow
-> Explores unusual metaphors, domains, wordplay
-> Presents best option with reasoning
```

**Example 3: Technical creativity**
```
User: "deep thinking this architecture problem"
-> Invokes TechnicalCreativity workflow
-> Uses systematic creativity for algorithmic/architecture work
-> Returns novel technical solution
```

---

**Attribution:** Adapted from PAI v5.0.0 BeCreative skill (Daniel Miessler, MIT-licensed). De-PAI'd for Jack's multi-agent fleet — no Pulse daemon, no bun runtime, no voice notification hooks, no execution log.
