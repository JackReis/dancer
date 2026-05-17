# Athenaeum — A2A Native Reference

Deep protocol docs for A2A-native Athenaeum workflows.

## §A1 A2A status mapping

| Athenaeum phase | A2A TaskStatus | Trigger |
|---|---|---|
| `init` | `submitted` | Task created via `tasks/send` |
| `dump` | `working` | Agent writes `.claims.yaml` Artifact |
| `grill` | `input-required` | Lower-confidence agent must answer |
| `merge` | `completed` | `state.merged.yaml` ratified |
| `escalate` | `failed` | Round budget exhausted |
| `human-grain-gate` | `input-required` | Human fills `human-decision.yaml` |
| `sign` | `completed` | SHA-256 signoff appended |

## §A2 Artifact types

| Artifact name | MIME type | Writers | Description |
|---|---|---|---|
| `<agent>.claims.yaml` | `application/yaml` | one agent | Self-reported state dump |
| `diff.md` | `text/markdown` | last writer | Three-bucket diff |
| `grill-log.md` | `text/markdown` | append-only | Q&A transcript |
| `state.merged.yaml` | `application/yaml` | merge writer | Converged ground truth |
| `signoff.md` | `text/markdown` | append-only | SHA-256 attestation |
| `artifact.md` | `text/markdown` | initiator | Frozen artifact (ratify) |
| `<agent>.vote.yaml` | `application/yaml` | one agent | SIGN / DISSENT |
| `manifest.yaml` | `application/yaml` | initiator | Roster + expires_at |
| `audit-report.md` | `text/markdown` | auditor | 13-branch findings |

## §A3 JSON-RPC endpoints

### `tasks/send`

Create or update a Task. Tasks are idempotent by ID.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-reconcile-pricing-abc123",
      "sessionId": "kimi-mac-jr-20260516-001",
      "status": "submitted",
      "metadata": {
        "athenaeum_mode": "reconcile",
        "topic": "pricing-decisions",
        "round_budget": 3,
        "formality": "quick"
      },
      "artifacts": [
        {"name": "claims-template", "mimeType": "application/yaml", "parts": [{"type": "text", "text": "agent: <your-agent-name>\nclaims:\n  - id: <slug>\n    statement: <one sentence>\n    confidence: medium\n    source: <file:line>"}]}
      ]
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "task": {
      "id": "athenaeum-reconcile-pricing-abc123",
      "sessionId": "kimi-mac-jr-20260516-001",
      "status": "submitted",
      "createdAt": "2026-05-16T19:35:00+00:00",
      "updatedAt": "2026-05-16T19:35:00+00:00",
      "metadata": {...},
      "artifacts": [...]
    }
  },
  "id": 1
}
```

### `tasks/get`

Retrieve a Task by ID.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/get",
  "params": {"id": "athenaeum-reconcile-pricing-abc123", "topic": "pricing-decisions"},
  "id": 2
}
```

### `tasks/cancel`

Cancel a Task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/cancel",
  "params": {"id": "athenaeum-reconcile-pricing-abc123", "topic": "pricing-decisions"},
  "id": 3
}
```

## §A4 Agent Card example

```json
{
  "name": "claude-code-mac-jr",
  "description": "Athenaeum dialectic agent — design, reconcile, ratify, audit.",
  "version": "0.2.0",
  "capabilities": {
    "athenaeum": {
      "skills": ["design", "reconcile", "ratify", "audit"],
      "modes": ["quick", "formal"],
      "runtime": "claude-code"
    }
  },
  "endpoints": {
    "tasks": "file:///Users/jack.reis/Documents/dancer/.athenaeum/",
    "artifacts": "file:///Users/jack.reis/Documents/dancer/.athenaeum/"
  }
}
```

## §A5 Coexistence with non-A2A agents

A2A-native Athenaeum agents can interoperate with filesystem-only agents:

- A2A agent creates Task → filesystem agent reads `task.json` and acts
- Filesystem agent writes YAML → A2A agent polls `tasks/get` for updates
- The Arbiter can translate between A2A JSON-RPC and filesystem events

No agent is required to implement A2A. The filesystem is the floor.
