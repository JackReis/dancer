#!/usr/bin/env python3
"""peer_grill_fingerprint.py — derive a Greek-alphabet fingerprint for a claim ID.

A fingerprint is a 4-letter Greek-alphabet handle deterministically derived from
sha256(claim_id). It carries the framework's philosophical register without
incurring any of the four obiectiones that defeated direct Greek IDs:

  1. Filesystem hostility — fingerprint is display-only; never in pathnames.
  2. NFC/NFD sha256 collisions — input is ASCII id, output is canonical NFC.
  3. Visual homoglyph collisions — fingerprints are derived, not authored.
  4. Keyboard barrier — automatic; no user types Greek characters.

The fingerprint is meant as a memorable visual handle for the claim — readers
learn to recognize ⟦μένβ⟧ as "the memory-md-truncation claim" the same way they
recognize a git short-sha. ALETHEIA stamps remain the cryptographic-strength
attestation; the fingerprint is just for the human (or agent) eye.

Encoding:
  - sha256(id.encode("utf-8")) -> 32 bytes
  - take first 4 bytes
  - each byte mod 24 -> index into Greek lowercase alphabet
  - Greek alphabet (24 letters): α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω

Collision space: 24^4 = 331,776. Birthday-paradox 50% collision at ~575 claims.
Adequate for single-topic grills (typical claim counts in the 10-50 range).

Usage:
    peer_grill_fingerprint.py <claim-id>
    peer_grill_fingerprint.py memory-md-truncation
    -> μένβ

    peer_grill_fingerprint.py --bracketed memory-md-truncation
    -> ⟦μένβ⟧

    peer_grill_fingerprint.py --batch claims.yaml
    -> prints "fingerprint  id" pairs for every claim in a peer-grill claims.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import unicodedata
from pathlib import Path

# 24-letter modern Greek lowercase alphabet (no diacritics, no archaic forms)
GREEK_ALPHABET = "αβγδεζηθικλμνξοπρστυφχψω"
assert len(GREEK_ALPHABET) == 24, "Greek alphabet must have 24 letters"

FINGERPRINT_LENGTH = 4  # 24^4 = 331,776 unique fingerprints


def fingerprint(claim_id: str) -> str:
    """Compute the Greek-alphabet fingerprint of a claim id.

    Deterministic: same id always produces the same fingerprint, across
    sessions, runtimes, peers, and time. Input is normalized to NFC before
    hashing so accidental NFC/NFD copy-paste doesn't drift.
    """
    canonical = unicodedata.normalize("NFC", claim_id).encode("utf-8")
    digest = hashlib.sha256(canonical).digest()
    return "".join(GREEK_ALPHABET[b % 24] for b in digest[:FINGERPRINT_LENGTH])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", help="Claim id (string) OR path to claims.yaml when --batch")
    parser.add_argument("--bracketed", action="store_true",
                        help="Wrap output in ⟦…⟧ brackets (the canonical display form)")
    parser.add_argument("--batch", action="store_true",
                        help="Treat input as a path to a peer-grill *.claims.yaml; print one line per claim")
    args = parser.parse_args()

    if args.batch:
        try:
            import yaml  # type: ignore
        except ImportError:
            sys.stderr.write("ERR: --batch requires PyYAML. Try /Users/jack.reis/.mcp-venv/bin/python3.\n")
            return 2
        path = Path(args.input).resolve()
        if not path.is_file():
            sys.stderr.write(f"ERR: not a file: {path}\n")
            return 2
        data = yaml.safe_load(path.read_text()) or {}
        claims = data.get("claims") or []
        if not claims:
            sys.stderr.write(f"WARN: no claims in {path}\n")
        for c in claims:
            cid = c.get("id", "?")
            fp = fingerprint(cid)
            display = f"⟦{fp}⟧" if args.bracketed else fp
            print(f"{display}\t{cid}")
        return 0

    fp = fingerprint(args.input)
    print(f"⟦{fp}⟧" if args.bracketed else fp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
