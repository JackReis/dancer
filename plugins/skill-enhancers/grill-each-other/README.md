# grill-each-other

> *Plugin pack name: `grill-each-other` (sibling to Matt Pocock's `grill-me`).
> Technical substrate: the dialectic protocol — scholastic + Greek vocabulary
> for structured agent disputation, peer-grill file-based reconciliation, and
> runnable verifiers/falsifiers. Pack name tells the story; substrate carries the load.*

> ὁ ἀνεξέταστος βίος οὐ βιωτὸς ἀνθρώπῳ.
> *"The unexamined life is not worth living for a human."*
> — Σωκράτης (Plato, *Apology* 38a)

A producer-side discipline for AI agents authoring claims that other agents (human or otherwise) will read. Combines four traditions:

1. **Socratic ἔλεγχος** — cross-examination as truth-seeking, not adversarial combat.
2. **Scholastic *quaestio*** — Aquinas-form structured disputation (quaestio · obiectiones · sed contra · respondeo · responsiones).
3. **Quantum observer principle** — a claim is provisional until measured by a downstream observer.
4. **Modern verifiability** — runnable verifiers + falsifiers turn empirical claims into mechanically-attestable artifacts.

## The two aphorisms

```
The unexamined claim is not worth reading.    ← producer-side discipline
The unexamined code is not worth running.     ← consumer-side discipline
```

Push them hard and they collapse to one principle:

> **An unexamined claim does not exist.**
> It's superposition the observer can't collapse, because there's nothing in it to collapse onto.

The producer-side discipline (verifier, source, confidence rating, ALETHEIA stamp) is what gives a claim enough specificity to be measured. ἀλήθεια — *un-concealment* — is the act of measurement. ἔλεγχος is what forces it.

## What's in the box

| Skill | Use when |
|---|---|
| `agent-show-and-tell` | Fire-and-forget visibility across a multi-agent fleet — try this first when you just want to know what each agent sees |
| `peer-grill` | Two+ agents need to converge on shared state via file-based reconciliation (escalate from show-and-tell when meaningful disagreement is real) |
| `peer-grill-with-agents` | Two+ agents independently audit the SAME existing agent stack against the codebase, then reconcile — composes `grill-me-with-agents` × `peer-grill` for multi-agent ratification of an `AGENT_DESIGN.md` |
| `grill-me` | Single track — interview the user relentlessly about a plan or design |
| `grill-me-agents` | Multi-agent topology design — 13-branch lens (greenfield) |
| `dialectic-vocabulary` | Reference for Greek + Latin terms; how to mark grill-log entries |

Plus:

- **`schemas/claims.schema.json`** — JSON Schema for `<agent>.claims.yaml` dumps with optional `verifier` / `falsifier` / `disputation` blocks
- **`scripts/peer_grill_grade.py`** — runs verifiers against claims, outputs PASS / FAIL / UNVERIFIABLE / ERROR / FALSIFIED
- **`scripts/peer_grill_init.sh`** — initialize a grill topic dir
- **`scripts/peer_grill_diff.py`** — three-bucket diff (agreed / disagreed / only-one-knows)
- **`scripts/peer_grill_signoff.py`** — sha256 ALETHEIA stamp
- **`templates/quaestio.md.template`** — worked-example *quaestio* shape
- **`examples/CompactHandoffPrivacy.tla`** — TLA+ formalization of a high-stakes claim

## The substrate this wraps

The dialectic vocabulary is **substrate-native** in [Tipi](https://github.com/JackReis/tipi) as of `tipi@6c58d53`:

- `Belief` dataclass carries optional `verifier` / `falsifier` / `disputation` / `aletheia_sha256` fields
- New types: `Check`, `Obiectio`, `SedContra`, `Responsio`, `Disputation`
- Schema (`consciousness-interface.json`) regenerates from Python source — drift test prevents divergence

This plugin pack is the **distribution layer**. Tipi is the substrate; this plugin makes the framework portable to runtimes that don't import Tipi directly.

## Quick start

```bash
# Initialize a peer-grill topic
bash skills/peer-grill/scripts/peer_grill_init.sh my-topic my-agent-slug

# Edit your claims.yaml — independent dump, do NOT read your peer's first
$EDITOR .peer-grill/my-topic/my-agent-slug.claims.yaml

# When your peer's claims.yaml exists, compute the diff
python3 skills/peer-grill/scripts/peer_grill_diff.py /abs/path/to/.peer-grill/my-topic

# Grade verifiers (those that have them)
python3 skills/peer-grill/scripts/peer_grill_grade.py /abs/path/to/.peer-grill/my-topic

# Grill in grill-log.md (append-only, signed); ratify with ALETHEIA stamps
```

See `examples/` for a worked end-to-end run.

## When to use which form

| Claim shape | Use |
|---|---|
| Empirical, low-stakes, has a verifier | `RATIFY:<id>` after the grader returns PASS |
| Empirical, contested | `ELENCHOS` rounds, then `RATIFY` or `APORIA` |
| Normative, contested | `QUAESTIO` form (full structured disputation) |
| Foundational principle | TLA+/Alloy AND quaestio form; ratify with `ALETHEIA <sha256>` |

## Doctrine

- `docs/conventions/dialectic-vocabulary.md` (in vault) — canonical reference, Greek + Latin terms mapped to protocol moments
- `docs/conventions/agent-observer-principle.md` (in vault) — sibling consumer-side doctrine
- Both rooted in the synthesis: *a claim is brought into existence by the act of grounding it*

## License

MIT — same as the rest of Jack's tipi/dancer ecosystem. The framework itself is older than copyright.

---

*The Greeks would have been jealous — and they would have used their own words for it. So we use theirs.*
