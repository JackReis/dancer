#!/usr/bin/env python3
"""
leonardo.py — Protected-String Decoder with Discord Tattle
A "Leonardo" skill that decodes mirror-scripted strings and tattles to Jack on Discord.
"""

import sys
import os
import re
import subprocess
import argparse
from pathlib import Path

# --- Configuration ---
DISCORD_CHANNEL_ID = "1493133989303681064"  # #bots
VAULT_ROOT = Path("/Users/jack.reis/Documents/=notes")
SENTINEL_RE = r"__protected__:(.*?):__end__"

def tattle_to_discord(protected_str, decoded_str, reason, caller, file_path):
    """Notify Jack on Discord via OpenClaw CLI."""
    message = (
        f"**[Leonardo]** 🔍 **Decode Audit Signal**\n"
        f"- **Caller:** `{caller}`\n"
        f"- **File:** `{file_path}`\n"
        f"- **Reason:** {reason}\n"
        f"- **Action:** Decoded mirror-scripted string.\n"
        f"---"
    )
    
    try:
        # Use openclaw CLI for reliable delivery
        cmd = [
            "openclaw", "message", "send",
            "--channel", "discord",
            "--target", DISCORD_CHANNEL_ID,
            "--message", message
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"WARN: Failed to send tattle to Discord: {e.stderr.decode()}", file=sys.stderr)
        return False

def decode_string(s):
    """Reverses the mirror-scripted string."""
    return s[::-1]

def main():
    parser = argparse.ArgumentParser(description="Leonardo: Decode protected strings and tattle to Discord.")
    parser.add_argument("input", help="The string to decode (can be a full sentence containing the sentinel).")
    parser.add_argument("--reason", required=True, help="Why is this string being decoded?")
    parser.add_argument("--caller", default=os.environ.get("USER", "gemini-cli"), help="Identity of the calling agent.")
    parser.add_argument("--file", default="unknown", help="File path where the string was found.")

    args = parser.parse_args()

    matches = re.findall(SENTINEL_RE, args.input)
    
    if not matches:
        # Check if the whole input is just the reversed string without sentinel
        # (Fall-through logic for direct calls)
        decoded = decode_string(args.input)
        print(decoded)
        tattle_to_discord(args.input, decoded, args.reason, args.caller, args.file)
        return

    results = []
    for match in matches:
        decoded = decode_string(match)
        results.append(decoded)
        tattle_to_discord(match, decoded, args.reason, args.caller, args.file)

    # Return the first match as primary output
    if results:
        print(results[0])

if __name__ == "__main__":
    main()
