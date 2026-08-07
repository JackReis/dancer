---
name: evals
description: NOT PORTED as a skill — evaluated against Jack's existing eval/observability tooling and found to be fully covered. See decision below.
---

# Evals — Decision: Not Ported

**Status:** This skill was **evaluated but NOT ported** from PAI v5.0.0. The overlap with Jack's existing observability/eval tooling is high — duplicating it would add scaffolding without value.

## Rationale

PAI's Evals skill is a comprehensive AI agent evaluation framework with three grader types (code-based, model-based, human) and pass@k/pass^k scoring. It evaluates agent transcripts, tool-call sequences, and multi-turn conversations.

Jack's fleet already has equivalent or superior eval tooling:

| PAI Evals capability | Jack's equivalent | Verdict |
|---------------------|-------------------|---------|
| Code-based graders (string_match, regex_match, binary_tests, static_analysis, state_check, tool_calls) | Paperclip verifier harness, vitest, ESLint, TypeScript compiler checks | Covered |
| Model-based graders (llm_rubric, natural_language_assert, pairwise_comparison) | Hermes model reviews, Claude Code reviews, Gemini review passes | Covered |
| Human (gold standard) | Jack as final approver, explicit reviewer gate | Covered |
| pass@k / pass^k scoring | Paperclip issue acceptance criteria, verifier checks | Covered |
| Scenario simulation (multi-turn) | Agent dispatch with Agent(subagent_type=...) | Covered |
| Failure-to-task conversion | Paperclip child issue creation, bd task tracking | Covered |

## What IS ported

The **concept** of eval coverage is captured in Jack's existing `dialectic-vocabulary` and `peer-grill` skills, which provide the adversarial validation that Evals' TEST phase would. The `bitter-pill-engineering` skill provides instruction-set auditing (the mirror of eval quality gates).

If a future Jack-native eval framework needs a dedicated skill, it should be built from Jack's tooling reality, not PAI's.

## Reference

- PAI source: `~/pai-sandbox/PAI-installer/Releases/v5.0.0/.claude/skills/Evals/SKILL.md` (preserved in `=notes/resources/upstream-verbatim/pai-v5.0.0/skills/Evals/`)
- PAI Evals was a 100+ file TypeScript toolchain (`AlgorithmBridge.ts`, `ScenarioRunner.ts`, `PAIAgentAdapter.ts`, etc.) — far more surface area than Jack's needs warrant.
