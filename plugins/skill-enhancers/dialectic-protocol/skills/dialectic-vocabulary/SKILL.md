---
name: dialectic-vocabulary
description: Reference for the scholastic + Greek vocabulary used in peer-grill and grill-me-agents protocols. Use when an agent needs to know what ELENCHOS, QUAESTIO, SED-CONTRA, RESPONDEO, or ALETHEIA mean as grill-log tags, or when authoring a structured disputation.
---

# Dialectic Vocabulary

The vocabulary that names the moves of grilling. Greek for the soul of the inquiry, Latin for the form on the page.

## The synthesis

**An unexamined claim does not exist.** It's superposition the observer can't collapse, because there's nothing in it to collapse onto. The producer-side discipline (verifier, source, confidence rating, ALETHEIA stamp) is what gives a claim enough specificity to be measured.

This is the strong-form sibling of the observer-principle doctrine, applied one rung upstream:

| Frame | What it says |
|---|---|
| Observer principle (consumer) | Until a downstream reader independently verifies, the claim is provisional |
| Unexamined-claim (producer) | Until the claimant applies measurement-machinery, there is nothing for the observer to measure |
| Synthesis | A claim is brought into existence by the act of grounding it |

## Greek (act-of-inquiry register)

| Term | Transliteration | Meaning | Where in the protocol |
|---|---|---|---|
| διαλεκτική | dialektikē | The whole art of reasoning through dialogue | The peer-grill protocol itself |
| ἔλεγχος | elenchos | Socratic cross-examination | Grill rounds in `grill-log.md` |
| ἀλήθεια | alētheia | Truth as **un-concealment** | Ratification stamp on merged state |
| σύνθεσις | synthesis | Putting-together; convergence | The merged-state file |
| λόγος | logos | Word, reason, structured account | The claim — the account that must be defensible |
| ἀπορία | aporia | A puzzle without resolution | The `unresolved.md` outcome |

## Latin (scholastic disputation register)

A *quaestio* in Aquinas's *Summa Theologiae* has a fixed form. Each question gets:

| Term | Meaning | Where in the protocol |
|---|---|---|
| quaestio | The disputed thesis | Statement field of a contested claim |
| obiectio / obiectiones | Numbered objection(s) | Counter-claims from peer agents |
| sed contra | The strongest opposing argument | One designated counter with the highest authority |
| respondeo | The author's adjudicating response | Author's reply that resolves the dispute |
| responsiones | Per-objection replies | Detailed answers to each obiectio |

## Grill-log tags (canonical)

Use these as the prefix on grill-log entries:

| Tag | Meaning |
|---|---|
| `ELENCHOS` | A cross-examination question (round 1+) |
| `APORIA` | An impasse — escalating to `unresolved.md` |
| `ALETHEIA` | A ratification stamp; the claim is now considered unconcealed truth |
| `QUAESTIO` | Opening a structured disputation on a contested claim |
| `OBIECTIO:N` | Objection N to the open quaestio |
| `SED-CONTRA` | The strongest counter, designated |
| `RESPONDEO` | The author's adjudicating response |
| `RESPONSIONES` | Per-objection replies |
| `RATIFY:<id>` | Sign-off for routine claims that don't need full quaestio form |

The protocol keeps `RATIFY:` as the default for everyday claims. The Latin tags are reserved for **high-stakes claims** where the disputation form earns its overhead.

## When to use which form

| Claim shape | Use |
|---|---|
| Empirical, low-stakes, has a verifier | `RATIFY:<id>` after grader returns PASS |
| Empirical, contested | `ELENCHOS` rounds, then `RATIFY` or `APORIA` |
| Normative, contested | `QUAESTIO` form (full structured disputation) |
| Foundational principle | TLA+/Alloy AND quaestio form; ratify with `ALETHEIA <sha256>` |

## The ἀλήθεια stamp

When a claim moves to `state.merged.yaml`, append a line to `signoff.md`:

```
ALETHEIA <agent-name> <ISO-timestamp> sha256:<hex of merged statement>
```

ἀλήθεια is literally *un-forgetting* — the negation of λήθη (Lethe, the river of forgetting). To stamp it is to assert: *this claim has been examined; it is not concealed by appearance, fashion, or expedience.*

If two agents independently RATIFY the same merged statement but their ALETHEIA stamps' sha256s don't match, that's an integrity failure — the protocol fails loud rather than silently merging diverged state.

## See also

- `peer-grill` — file-based reconciliation protocol (this skill is its vocabulary reference)
- `grill-me` — single-track relentless interview
- `grill-me-agents` — 13-branch interview for multi-agent designs
- Substrate: [Tipi](https://github.com/JackReis/tipi) — the `Belief` dataclass carries `verifier` / `falsifier` / `disputation` / `aletheia_sha256` fields natively
- Vault doctrine: `docs/conventions/dialectic-vocabulary.md` (the canonical, longer-form version)

## What this is NOT

- **Not a religion or appeal to authority.** The form survived because it works, not because it's sacred.
- **Not a barrier to entry.** Plain `ELENCHOS` / `RATIFY` for everyday claims; the Latin form is reserved for stakes that earn it.
- **Not a substitute for verifiers.** A formally-disputed normative claim is still a value judgment; a formally-disputed empirical claim should also have a runnable verifier. The forms compose.
