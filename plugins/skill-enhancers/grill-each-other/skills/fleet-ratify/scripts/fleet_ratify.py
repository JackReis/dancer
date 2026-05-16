#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import os
import pathlib
import re
import sys

# Canonical Vault Root
VAULT_ROOT = pathlib.Path("/Users/jack.reis/Documents/=notes")
RATIFY_DIR = VAULT_ROOT / ".fleet-ratify"

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def log_event(topic_path, agent, event, detail=""):
    log_file = topic_path / "log.md"
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {agent} | {event}: {detail}\n"
    with log_file.open("a") as f:
        f.write(line)

def init(artifact_path, roster, topic=None, mode='standard'):
    artifact = pathlib.Path(artifact_path)
    if not artifact.exists():
        print(f"Error: Artifact {artifact_path} not found.")
        return 1
    
    if not topic:
        topic = artifact.stem
    
    topic_path = RATIFY_DIR / topic
    if topic_path.exists():
        # Handle collision
        i = ord('b')
        while topic_path.exists() and i <= ord('z'):
            topic_path = RATIFY_DIR / f"{topic}-{chr(i)}"
            i += 1
        if topic_path.exists():
            print(f"Error: Too many collisions for topic {topic}")
            return 1
    
    topic_path.mkdir(parents=True)
    
    # Copy artifact
    target_artifact = topic_path / "artifact.md"
    target_artifact.write_bytes(artifact.read_bytes())
    sha = get_sha256(target_artifact)
    
    # Write manifest
    expires_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=72)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Simplistic agent identity detection
    initiator = os.environ.get("AGENT_ID", "pt") # Default to pt for local CLI
    
    manifest_content = f"""topic: {topic_path.name}
initiator: {initiator}
artifact_sha256: {sha}
artifact_origin: {artifact.absolute()}
roster:
"""
    for agent in roster.split(','):
        manifest_content += f"  - {agent.strip()}\n"
    
    manifest_content += f"""expires_at: {expires_at}
mode: {mode}
status: open
"""
    (topic_path / "manifest.yaml").write_text(manifest_content)
    
    log_event(topic_path, initiator, "OPENED", f"artifact={artifact.name} sha256={sha[:8]}")
    print(f"Initialized ratification for '{topic_path.name}' at {topic_path}")
    return 0

def check():
    agent = os.environ.get("AGENT_ID", "pt")
    open_topics = []
    if not RATIFY_DIR.exists():
        return 0
    
    for topic_dir in RATIFY_DIR.iterdir():
        if not topic_dir.is_dir():
            continue
        manifest_file = topic_dir / "manifest.yaml"
        if not manifest_file.exists():
            continue
        
        content = manifest_file.read_text()
        status_match = re.search(r"status:\s*(\w+)", content)
        if status_match and status_match.group(1) != "open":
            continue
        
        roster_match = re.search(r"roster:(.*?)(?:\n\w+:|\Z)", content, re.DOTALL)
        if not roster_match:
            continue
        
        roster = [r.strip("- ").strip() for r in roster_match.group(1).strip().split("\n")]
        if agent in roster:
            vote_file = topic_dir / f"{agent}.vote.yaml"
            if not vote_file.exists():
                open_topics.append(topic_dir.name)
    
    if open_topics:
        print("Open ratifications awaiting your vote:")
        for t in open_topics:
            print(f"  - {t}")
    else:
        print("No open ratifications awaiting your vote.")
    return 0

def vote(topic_name, decision, dissent_reason=None):
    agent = os.environ.get("AGENT_ID", "pt")
    topic_path = RATIFY_DIR / topic_name
    if not topic_path.exists():
        print(f"Error: Topic {topic_name} not found.")
        return 1
    
    artifact_file = topic_path / "artifact.md"
    if not artifact_file.exists():
        print(f"Error: artifact.md missing in {topic_path}")
        return 1
    
    sha = get_sha256(artifact_file)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    vote_content = f"""agent: {agent}
artifact_sha256: {sha}
decision: {decision.upper()}
timestamp: {ts}
"""
    if decision.upper() == "DISSENT" and dissent_reason:
        vote_content += f"""dissent:
  - atom:
      section: "general"
      anchor: "entire document"
    objection: {dissent_reason}
    proposed_resolution: carve-caveat
"""
    
    (topic_path / f"{agent}.vote.yaml").write_text(vote_content)
    log_event(topic_path, agent, "VOTE", decision.upper())
    print(f"Cast {decision.upper()} vote for topic '{topic_name}'")
    return 0

def tally(topic_name):
    topic_path = RATIFY_DIR / topic_name
    if not topic_path.exists():
        print(f"Error: Topic {topic_name} not found.")
        return 1
    
    manifest_file = topic_path / "manifest.yaml"
    if not manifest_file.exists():
        print(f"Error: manifest.yaml missing.")
        return 1
    
    manifest_content = manifest_file.read_text()
    roster_match = re.search(r"roster:(.*?)(?:\n\w+:|\Z)", manifest_content, re.DOTALL)
    if not roster_match:
        print("Error: Could not parse roster.")
        return 1
    roster = [r.strip("- ").strip() for r in roster_match.group(1).strip().split("\n")]
    
    votes = {}
    voted_agents = []
    for agent in roster:
        vote_file = topic_path / f"{agent}.vote.yaml"
        if vote_file.exists():
            voted_agents.append(agent)
            vote_content = vote_file.read_text()
            decision_match = re.search(r"decision:\s*(\w+)", vote_content)
            if decision_match:
                votes[agent] = decision_match.group(1).upper()
    
    if not voted_agents:
        print("No votes cast yet.")
        return 0
    
    # Determine merge writer
    voted_agents.sort()
    merge_writer = voted_agents[0]
    current_agent = os.environ.get("AGENT_ID", "pt")
    
    if current_agent != merge_writer:
        print(f"Merge writer is {merge_writer}. Current agent {current_agent} is not responsible for tallying.")
        # But we might tally anyway if expires_at passed?
        # For now, follow the rule.
        return 0

    all_signed = all(votes.get(a) == "SIGN" for a in roster)
    
    if all_signed:
        # Finalize
        sha_match = re.search(r"artifact_sha256:\s*(\w+)", manifest_content)
        sha = sha_match.group(1) if sha_match else "unknown"
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        ratified_content = f"""# Ratified: {topic_name}
artifact_sha256: {sha}
ratified_on: {ts}

## Signatures
"""
        for agent in roster:
            ratified_content += f"- {agent} signed at {ts} (sha256: {sha})\n"
        
        (topic_path / "ratified.md").write_text(ratified_content)
        
        # Update manifest status
        new_manifest = re.sub(r"status:\s*\w+", "status: ratified", manifest_content)
        manifest_file.write_text(new_manifest)
        
        log_event(topic_path, merge_writer, "RATIFIED")
        print(f"Topic '{topic_name}' RATIFIED!")
    else:
        # Decompose or pending-human
        print(f"Topic '{topic_name}' has dissent or missing votes. Triggering decomposition preview.")
        
        # Simple decomposition.md
        decomp_content = f"# Decomposition Preview: {topic_name}\n\n"
        decomp_content += "Some agents have dissented or not yet voted.\n\n"
        decomp_content += "## Votes\n"
        for a in roster:
            decomp_content += f"- {a}: {votes.get(a, 'PENDING')}\n"
        
        (topic_path / "decomposition.md").write_text(decomp_content)
        
        # human-decision.yaml
        decision_stub = f"""topic: {topic_name}
decision:             # accept-split | decompose-further | rewrite-with-caveats | reject
notes: ""
"""
        (topic_path / "human-decision.yaml").write_text(decision_stub)
        
        # Update manifest status
        new_manifest = re.sub(r"status:\s*\w+", "status: pending-human", manifest_content)
        manifest_file.write_text(new_manifest)
        
        log_event(topic_path, merge_writer, "DECOMPOSED")
        print(f"Topic '{topic_name}' DECOMPOSED. Awaiting human decision.")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fleet Ratification Utility")
    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("artifact")
    init_parser.add_argument("--roster", required=True)
    init_parser.add_argument("--topic")
    init_parser.add_argument("--mode", default="standard")
    
    check_parser = subparsers.add_parser("check")
    
    vote_parser = subparsers.add_parser("vote")
    vote_parser.add_argument("topic")
    vote_parser.add_argument("decision", choices=["sign", "dissent"])
    vote_parser.add_argument("--reason")
    
    tally_parser = subparsers.add_parser("tally")
    tally_parser.add_argument("topic")
    
    args = parser.parse_args()
    
    if args.command == "init":
        sys.exit(init(args.artifact, args.roster, args.topic, args.mode))
    elif args.command == "check":
        sys.exit(check())
    elif args.command == "vote":
        sys.exit(vote(args.topic, args.decision, args.reason))
    elif args.command == "tally":
        sys.exit(tally(args.topic))
    else:
        parser.print_help()
