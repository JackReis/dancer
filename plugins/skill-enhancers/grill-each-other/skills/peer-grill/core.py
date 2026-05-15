# peer_grill/core.py

import os
from datetime import datetime

# Import local modules we plan to create
from .state_manager import ClaimsStateManager
from .crypto_utils import AttestationManager
from .dialectics import DialecticProcessor

# --- Configuration ---
CLAIM_DUMP_FILE = "claim_dump.log"
LOG_FILE_PREFIX = "grill_session-"
MAX_LOG_LINES = 1000

def initialize_grill_session(agents: list[str], initial_claims: str) -> str:
    """
    Initializes a new peer-grill session, sets up persistent logs, and dumps initial claims.

    :param agents: List of agents participating in the grid.
    :param initial_claims: Raw string of initial claims (e.g., "Claim A: X is true. Claim B: Y requires Z.")
    :return: The filename/path of the session's current log state.
    """
    session_id = datetime.now().strftime("%Y%m%d%H%M%S")
    log_filename = f"{LOG_FILE_PREFIX}{session_id}.log"

    print(f"--- Initiating Peer-Grill Session: {session_id} ---")
    print(f"Agents: {', '.join(agents)}")
    print(f"Objective: Challenge and ratify core axioms.")

    # 1. Initialize the State Manager
    state_manager = ClaimsStateManager(log_filename, max_lines=MAX_LOG_LINES)
    
    # 2. Dump Initial Claims
    claims_to_dump = initial_claims.strip()
    state_manager.dump_claims(claims_to_dump, agents)
    
    print(f"[INITIALIZED] Claims successfully written to {log_filename}.")
    return log_filename


def execute_grilling_cycle(log_filename: str, agent_input: str, current_agent: str) -> str:
    """
    Processes a single input from one agent, conducting the rebuttal and logging the result.

    :param log_filename: The persistent log file tracking the session.
    :param agent_input: The agent's input containing the challenge/rebuttal.
    :param current_agent: The name of the agent making the input.
    :return: A message confirming the logging and next steps.
    """
    print(f"\n--- Processing Input from {current_agent} ---")

    if not os.path.exists(log_filename):
        return "Error: Session log file not found. Must initialize the session first."

    try:
        # 1. Process the challenge dialectically
        dialectics = DialecticProcessor()
        processed_challenge = dialectics.structure_challenge(agent_input)

        # 2. Record the event
        state_manager = ClaimsStateManager(log_filename)
        
        # Log the round, including the processing of the challenge
        log_record = f"\n\n--- ROUND START: {current_agent} challenges existing claims ---\n"
        log_record += f"AGENT: {current_agent}\n"
        log_record += f"CHALLENGE: {processed_challenge}\n"
        
        state_manager.append_to_log(log_record)
        
        # 3. Re-attest the state of the claims after the intervention
        attestator = AttestationManager()
        new_attestations = attestator.re_attest(log_filename)
        
        return f"✅ Round completed by {current_agent}. New attestations recorded: {new_attestations}"

    except Exception as e:
        print(f"An error occurred during the grilling cycle: {e}")
        return f"❌ Error during cycle: {e}"


def ratify_and_finish(log_filename: str) -> str:
    """
    Finalizes the session by compiling the final knowledge graph and ratifying the surviving claims.
    """
    print("\n=================================================================")
    print("             🌟 ATTEMPTING FINAL RATIFICATION 🌟            ")
    print("=================================================================")

    try:
        state_manager = ClaimsStateManager(log_filename)
        # This relies on crypto_utils providing the final review
        attestator = AttestationManager()
        final_claims, final_hashes = attestator.finalize_ratification(log_filename)

        report = f"\n✅ *** PEER-GRILL SESSION COMPLETE ***\n"
        report += f"Source Log: {log_filename}\n"
        report += "-----------------------------------------------------\n"
        report += "FINAL RATIFIED CLAIMS (Verifiable through SHA256):\n"
        for claim, hash_val in final_claims.items():
            report += f" - [CLAIM] {claim}\n"
            report += f"   [ATTESTATION]: {hash_val}\n"
        report += "-----------------------------------------------------\n"
        report += "Synthesis complete. The true understanding emerges from the conflict."
        return report
        
    except Exception as e:
        return f"❌ FATAL ERROR: Could not ratify claims. {e}"


# ====================================================================
# ENTRY POINT HANDLER (Mock for agent framework integration)
# ====================================================================
def run_peer_grill(agents: list[str], initial_claims: str, rebuttal_input: str = None):
    """
    The primary function called by the agent ecosystem to run the protocol.
    """
    if not initial_claims:
        return "Error: Must provide initial claims to begin the session."
    
    # 1. Setup
    log_file = initialize_grill_session(agents, initial_claims)
    session_result = f"Session initialized. Current status logged in {log_file}\n"

    # 2. Handle Rebuttal (if provided in a single call)
    if rebuttal_input:
        session_result += execute_grilling_cycle(log_file, rebuttal_input, "SYSTEM/User Input")
    
    # 3. Finalization (A full cycle would require iterative calls, but we demonstrate the end goal)
    final_report = ratify_and_finish(log_file)
    session_result += final_report
    
    return session_result

# Example usage (for testing/demonstration):
if __name__ == "__main__":
    agents_list = ["Agent A", "Agent B"]
    claims = "Initial theory is that all self-correcting systems use a centralized scheduler. A second premise is that the system requires asynchronous communication."
    
    # PHASE 1: Run the setup and an initial challenge
    initial_output = run_peer_grill(agents_list, claims)
    print("\n--- OUTPUT ---")
    print(initial_output)
    
    # PHASE 2: Simulate a rebuttal from Agent A
    rebuttal = "The premise that scheduling must be centralized is flawed. A federation of decoupled autonomous modules achieves the same goal with greater resilience (SED CONTRA)."
    
    # NOTE: In a real agent loop, the log_file from step 1 would be passed here
    # For simplicity, we re-run the setup to get the file path for demonstration
    test_file = initialize_grill_session(agents_list, claims)
    
    # Run the rebuttal on the newly created session file
    rebuttal_output = execute_grilling_cycle(test_file, rebuttal, "Agent A")
    print("\n--- OUTPUT ---")
    print(rebuttal_output)
    
    # PHASE 3: Ratify
    final_report = ratify_and_finish(test_file)
    print("\n--- OUTPUT ---")
    print(final_report)