# peer_grill/consensus_manager.py

from .state_manager import ClaimsStateManager
from typing import Dict

class ConsensusManager:
    """
    The Governor for the peer-grill protocol. 
    This module analyzes the immutable log state to diagnose the current level 
    of consensus, identify points of divergence, and suggest the next most valuable 
    intellectual action (e.g., calling another skill, pausing, or ratifying).
    """
    
    def __init__(self, state_manager: ClaimsStateManager):
        """Initializes the manager with access to the session's state."""
        self.state_manager = state_manager
        self.MAX_CONSENSUAL_GAP = 3 # Number of rounds/inputs required before considering a consensus path

    @staticmethod
    def _calculate_divergence_score(history: str) -> float:
        """
        Analyzes the text volume to estimate the intellectual friction.
        High volume = High dialectical effort. High keyword count = High focus.
        """
        # Advanced NLP/LM logic would go here.
        # Simple implementation for concept: Count explicit contradiction markers.
        contradictions = len(re.findall(r'contradicts|sed contra|therefore but', history, re.IGNORECASE))
        
        # Normalizing score: 0.0 (No debate) to 1.0 (Maximum conflict)
        return min(1.0, contradictions * 0.2 + len(history.split('\n')) / 100.0)

    def analyze_consensus(self) -> Dict:
        """
        Analyzes the current log state to diagnose the state of agreement.

        :return: A dictionary containing key diagnostics (level, divergence, suggested action).
        """
        history = self.state_manager.get_history()
        if "Error: State log file does not exist" in history:
            return {"status": "ABORTED", "message": "Cannot analyze consensus. Session history is missing."}

        divergence_score = self._calculate_divergence_score(history)
        
        # --- Consensus Logic Tree ---
        
        # 1. Deadlock Detection (High divergence + lack of clear path forward)
        if divergence_score > 0.8:
            action = "DEADLOCK DETECTED: The claims are fundamentally irreducible via pure dialectic. Require external proof (e.g., running a system test or querying the knowledge graph)."
            return {"status": "DEADLOCK", "score": divergence_score, "action": action}

        # 2. Consensus Detection (Low divergence + sustained effort)
        elif divergence_score < 0.3 and len(history.split('\n')) > 20:
            action = "HIGH LIKELIHOOD OF CONSENSUS: The persistent agreement on underlying core axioms suggests the debate can now advance to system-level ratification."
            return {"status": "NEAR_CONSENSUS", "score": divergence_score, "action": "Trigger final_ratification()."}

        # 3. Ongoing Debate (Normal state)
        else:
            action = f"OPEN DISPUTE: Progress is active. Continue grilling on the specific point of contention. Next goal: Increase the conceptual velocity on a specific claim."
            return {"status": "OPEN_DISPUTE", "score": divergence_score, "action": action}

    def get_next_action(self) -> str:
        """
        Determines the most optimal next conversational flow based on current analysis.
        This function is the 'brain' of the skill.
        """
        analysis = self.analyze_consensus()
        
        if analysis["status"] == "DEADLOCK":
            # Trigger external skill calls
            return "ATTENTION: System recommends activating `gitnexus-impact-analysis` or `gitnexus-exploring` to resolve the conceptual deadlock."
        
        elif analysis["status"] == "NEAR_CONSENSUS":
            # Trigger the finalization step
            return "SUCCESS: Consensus is near. Proceed to final ratification using `finalize_ratification()` to commit the current understanding."
        
        else:
            # Continue current cycle
            return f"CONTINUE: {analysis['action']}"

    def __repr__(self) -> str:
        return "<ConsensusManager: Protocol Governor>"