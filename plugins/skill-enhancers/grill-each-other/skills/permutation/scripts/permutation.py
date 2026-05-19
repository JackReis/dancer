#!/usr/bin/env python3
"""Permutation — Generate visual topology diagrams from ratified agent matrices.

Outputs Mermaid (default) and ASCII formats.
Each agent node includes a signed SHA-256 of its ratified row.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def parse_matrix_json(data: dict) -> list[dict]:
    """Parse a ratified-matrix.json into a list of relationship dicts.

    Expected format:
    {
        "agents": ["ARBITER", "HERMES", ...],
        "relationships": [
            {"from": "ARBITER", "to": "HERMES", "contract": "dispatch_envelope", "status": "ratified"},
            ...
        ]
    }
    """
    agents = data.get("agents", [])
    relationships = data.get("relationships", [])
    return [{"agents": agents, "relationships": relationships}]


def parse_matrix_md(content: str) -> dict:
    """Parse a ratified-matrix.md markdown table into structured data.

    Handles pipe-delimited tables with headers like:
    | Agent | Provides | Expects | Status |
    """
    agents = set()
    relationships = []
    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("|---") or line.startswith("| ==="):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 4 and cells[0] not in ("Agent", "From", ""):
                from_agent = cells[0]
                provides = cells[1] if len(cells) > 1 else ""
                expects = cells[2] if len(cells) > 2 else ""
                status = cells[3] if len(cells) > 3 else "ratified"
                target = cells[4] if len(cells) > 4 else ""
                agents.add(from_agent)
                if target:
                    agents.add(target)
                relationships.append({
                    "from": from_agent,
                    "to": target or "UNKNOWN",
                    "contract": provides or expects,
                    "status": status.lower(),
                })

    return {"agents": sorted(agents), "relationships": relationships}


def compute_row_signature(agent: str, relationships: list[dict]) -> str:
    """Compute SHA-256 of an agent's ratified row for node signing."""
    row_data = json.dumps(
        sorted([r for r in relationships if r["from"] == agent or r["to"] == agent],
               key=lambda x: str(x)),
        sort_keys=True,
    )
    return hashlib.sha256(row_data.encode()).hexdigest()[:12]


def generate_mermaid(data: dict) -> str:
    """Generate a Mermaid graph LR diagram from parsed matrix data."""
    agents = data.get("agents", [])
    relationships = data.get("relationships", [])

    lines = ["graph LR"]

    agent_signatures = {}
    agent_has_dissent = set()

    for rel in relationships:
        if rel.get("status") in ("dissent", "misaligned", "divergent"):
            agent_has_dissent.add(rel["from"])
            agent_has_dissent.add(rel["to"])

    for agent in agents:
        sig = compute_row_signature(agent, relationships)
        agent_signatures[agent] = sig

    for rel in relationships:
        from_agent = rel["from"]
        to_agent = rel["to"]
        contract = rel.get("contract", "")
        status = rel.get("status", "ratified")

        if status in ("ratified", "confirmed"):
            if contract:
                lines.append(f"    {from_agent} ---|{contract}|--> {to_agent}")
            else:
                lines.append(f"    {from_agent} --- {to_agent}")
        elif status in ("dissent", "misaligned", "divergent"):
            if contract:
                lines.append(f"    {from_agent} -.->|dissent: {contract}|--> {to_agent}")
            else:
                lines.append(f"    {from_agent} -.-> {to_agent}")
        else:
            if contract:
                lines.append(f"    {from_agent} -.-|{contract}|--> {to_agent}")
            else:
                lines.append(f"    {from_agent} -.- {to_agent}")

    lines.append("")

    for agent in agents:
        sig = agent_signatures.get(agent, "unknown")
        if agent in agent_has_dissent:
            lines.append(f"    style {agent} fill:#FFC107,stroke:#FF6F00")
        else:
            lines.append(f"    style {agent} fill:#4CAF50,stroke:#2E7D32")

    lines.append("")
    lines.append("%% Node Signatures (SHA-256 of ratified row)")
    for agent in agents:
        lines.append(f"%% {agent}: sig={agent_signatures.get(agent, 'unknown')}")

    return "\n".join(lines)


def generate_ascii(data: dict) -> str:
    """Generate an ASCII topology diagram from parsed matrix data."""
    agents = data.get("agents", [])
    relationships = data.get("relationships", [])

    lines = ["Topology:", "=" * 60]

    agent_signatures = {}
    for agent in agents:
        sig = compute_row_signature(agent, relationships)
        agent_signatures[agent] = sig

    for rel in relationships:
        from_agent = rel["from"]
        to_agent = rel["to"]
        contract = rel.get("contract", "")
        status = rel.get("status", "ratified")

        if status in ("ratified", "confirmed"):
            marker = "---"
            label = f"[{contract}]" if contract else ""
        elif status in ("dissent", "misaligned", "divergent"):
            marker = "-X-"
            label = f"[Dissent: {contract}]" if contract else " [DISSENT]"
        else:
            marker = "-?-"
            label = f"[{contract}]" if contract else " [unconfirmed]"

        lines.append(f"  {from_agent} {marker} {label} --> {to_agent}")

    lines.append("")
    lines.append("Node Signatures (SHA-256 of row):")
    for agent in agents:
        lines.append(f"  {agent}: sig={agent_signatures.get(agent, 'unknown')}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Permutation — visual topology output")
    parser.add_argument("--input", required=True, help="Path to ratified-matrix.json or .md")
    parser.add_argument("--format", choices=["mermaid", "ascii"], default="mermaid",
                        help="Output format (default: mermaid)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    content = input_path.read_text(encoding="utf-8")

    if input_path.suffix == ".json":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON: {exc}", file=sys.stderr)
            return 1
        parsed = parse_matrix_json(data)
        matrix_data = parsed[0] if parsed else {"agents": [], "relationships": []}
    else:
        matrix_data = parse_matrix_md(content)

    if args.format == "mermaid":
        output = generate_mermaid(matrix_data)
    else:
        output = generate_ascii(matrix_data)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())