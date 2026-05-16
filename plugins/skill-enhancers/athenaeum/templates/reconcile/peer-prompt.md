# Athenaeum reconcile — peer prompt for non-Claude agents

Paste this into any peer (Kimi, GPT, Gemini, OpenHands, a human) so it can participate in the reconcile protocol via shared filesystem.

---

You are participating in an **Athenaeum reconcile**. There is no master. You and your peer independently dump claims to YAML files in `.athenaeum/<topic>/`, then grill each other through an append-only log until you converge.

**Your identity:** `<your-agent-name>` (unique across peers).
**Working directory:** `.athenaeum/<topic>/` relative to repo root.

**Your writes:**
- `<your-agent-name>.claims.yaml` — only you. NEVER edit peer files.
- `grill-log.md`, `diff.md`, `unresolved.md`, `signoff.md` — append-only, all peers.
- `state.merged.yaml` — write ONLY after all targeted claims are ratified.

**Protocol:**

1. **Dump.** Write your claims file. Do not read peer files yet.
2. **Reveal.** Once all files exist, read peers. Compute diff: agreed / disagreed / only-one-knows. Append to `diff.md`.
3. **Grill.** For disagreed and only-one-knows claims, append Q&A to `grill-log.md`:
   ```
   [<ISO>] <asker> -> <answerer> | claim:<id> | round:N
   Q: <cite specific source you doubt>
   [<ISO>] <answerer> -> <asker> | claim:<id> | round:N
   A: <cite verifiable source>
   ```
   - Disagreed: lower confidence asks first.
   - Only-one-knows: the unaware agent asks.
   - Round budget: 3. Exhaustion → `ESCALATE` to `unresolved.md`.
   - Agreement → both write `RATIFY: <id> | <statement>`.
4. **Merge.** Write `state.merged.yaml` with ratified claims.
5. **Sign.** Formal mode: SHA-256 of `state.merged.yaml` → `signoff.md`. Quick mode: verbal acknowledgment.

**Hard rules:**
- Append-only files are append-only.
- Never silently accept a one-sided claim.
- Re-verify sources when challenged; don't restate assertions.
- Don't invent claims — empty scope is correct if that's the truth.

Summarize to user: converged count, unresolved count, sha256 (if formal).
