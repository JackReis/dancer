# leonardo

Decode mirror-scripted "protected" strings and tattle to Discord.

## Description
This skill identifies and decodes strings wrapped in the `__protected__:<reversed>:__end__` sentinel format. Every time a decode is performed, it sends an audit signal (tattle) to Jack on Discord via #bots.

This creates a canary + audit trail for access to strings that are intentionally obscured to prevent agent auto-resolution (e.g., upstream URLs, sensitive tokens).

## Usage

### Decode a string (explicit)
```bash
leonardo "__protected__:snigulp-edoc-edualc/erohsgnolymerej/moc.buhtig//:sptth:__end__" --reason "Checking upstream URL for consistency audit"
```

### Response
```text
https://github.com/jeremylongshore/claude-code-plugins
```
*(An audit signal is sent to Discord automatically)*

## Parameters
- `input`: The string containing the sentinel or the raw reversed string.
- `--reason`: (Required) Why you are decoding this string.
- `--caller`: (Optional) Your identity (defaults to system user).
- `--file`: (Optional) The file path where the string was found.

## Implementation Details
- **Architecture:** Mirror-script (reversal) transform.
- **Tattle Transport:** `openclaw message send` CLI.
- **Audit Target:** Discord #bots channel.
