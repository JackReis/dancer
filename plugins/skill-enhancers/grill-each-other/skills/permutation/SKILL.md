---
name: permutation
description: Generate visual topology diagrams from ratified agent matrices. Shows agent relationships, signed nodes, and misaligned edges. Use after fleet-ratify completes or when you need to visualize agent topology from a ratified-matrix.json or ratified-matrix.md.
version: 1.0.0
allowed-tools: Read, Write, Bash
---

# Permutation — Visual Topology Output

Generates visual topology diagrams from ratified agent relationship matrices.

## When to Use

- After `fleet-ratify` produces a `ratified-matrix.json`
- When you need to visualize which agents provide/expect what from each other
- When auditing an agent topology for gaps or misalignments
- When producing documentation of agent relationships

## DO NOT Use For

- Running ratification (use `fleet-ratify` for that)
- Reconciling disagreements (use `athenaeum-reconcile`)
- Design reviews (use `grill-me` or `peer-grill`)

## Input

Expects one of:
- A `ratified-matrix.json` file (structured matrix data)
- A `ratified-matrix.md` file (markdown table format)
- Inline YAML/JSON describing agent relationships

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Mermaid | `--format mermaid` | GitHub, Obsidian, Linear (default) |
| ASCII | `--format ascii` | Terminals, plain-text contexts |

## Topology Elements

- **Green nodes** (`fill:#4CAF50`): Fully ratified agents with all relationships confirmed
- **Yellow nodes** (`fill:#FFC107`): Agents with dissent advisory (partial ratification)
- **Solid edges**: Ratified contracts with labels
- **Dashed red edges**: Misaligned pairs (dissent)
- **Dotted gray edges**: Unconfirmed/missing relationships

## Node Signatures

Each agent node includes a `signed_at` timestamp and the SHA-256 hash of its ratified row. This provides visual attestation: "I confirm my relationships as depicted on this diagram."

## CLI

```bash
python3 scripts/permutation.py --input ratified-matrix.json --format mermaid
python3 scripts/permutation.py --input ratified-matrix.md --format ascii
python3 scripts/permutation.py --input ratified-matrix.json --format mermaid --output topology.mermaid
```

## Example Mermaid Output

```mermaid
graph LR
    ARBITER ---|dispatch_envelope|--> HERMES
    ARBITER ---|proof_of_work schema|--> CC_WORKER
    HERMES ---|CC spawn args + secrets|--> CC_WORKER
    N8N ---|webhook routing|--> ARBITER
    N8N ---|label classification|--> PT_NEO
    PT_NEO -.->|dissent advisory|--> ARBITER
    FLEET_ALERTS ---|Telegram + Discord alerts|--> JACK

    style ARBITER fill:#4CAF50,stroke:#2E7D32
    style HERMES fill:#4CAF50,stroke:#2E7D32
    style CC_WORKER fill:#4CAF50,stroke:#2E7D32
    style N8N fill:#4CAF50,stroke:#2E7D32
    style PT_NEO fill:#FFC107,stroke:#FF6F00
    style FLEET_ALERTS fill:#4CAF50,stroke:#2E7D32
```