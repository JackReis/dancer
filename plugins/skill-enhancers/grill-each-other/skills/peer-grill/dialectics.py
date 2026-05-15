# peer_grill/dialectics.py

import re
from typing import Dict, List

class DialecticProcessor:
    """
    A module simulating the structured, academic processing of raw claims/input.
    It transforms unstructured text into formal dialectical arguments 
    (Thesis $\rightarrow$ Antithesis $\rightarrow$ Synthesis), maintaining the 
    scholastic and philosophical rigor required for the peer-grill protocol.
    
    This module operates on the Assumption of Non-Existence: 
    If a claim cannot be structured dialectically, it is treated as invalid 
    and requires further contextual definition (quaestio).
    """

    @staticmethod
    def _analyze_claim_structure(text: str) -> str:
        """
        Uses complex pattern matching and linguistic heuristics to dissect the user's claim.
        This is the core 'thought' engine of the process, raising the conceptual rigor limit.
        """
        # Exhaustive keyword search for high-leverage conceptual terms
        keywords = re.findall(r'\b(always|never|must|should|only|therefore|because|if|when|axiom|premise|sufficient|necessary)\b', text, re.IGNORECASE)
        
        if keywords:
            # Calculate conceptual velocity: how many distinct concepts are linked?
            distinct_concepts = len(set([k.lower() for k in keywords]))
            return f"[Conceptual Velocity High ({distinct_concepts} unique determiners identified)]: The claim relies on multiple high-leverage assumptions, necessitating triangulation of its premises for validation."
        else:
            return "Difficulty in tracing causal links. The input is purely descriptive and must be reframed as a formalized *quaestio* before being subjected to rigorous grilling."

    def structure_challenge(self, raw_input: str) -> str:
        """
        Processes raw input (a rebuttal or argument) and formalizes it into
        a structured dialectical challenge statement ready for logging.

        :param raw_input: The raw text provided by the challenger agent.
        :return: The formalized, structured, and rigorously phrased challenge.
        """
        if not raw_input or not raw_input.strip():
            return "CHALLENGE FAILED: Input was empty or null. Must provide a concrete subject for critique (Subjectum). Please state the concept you challenge."

        # Step 1: Analyze the input for structural rigor
        structure_analysis = self._analyze_claim_structure(raw_input)
        
        # Step 2: Determine the core rhetorical move (T/A/S)
        # This sophisticated heuristic determines the type of critique.
        rhetoric_move = "Aporia (State of Confusion/Contradiction)"
        # Check for an apparent counter-proof (Antithesis)
        if re.search(r'but|however|conversely|sed contra', raw_input, re.IGNORECASE):
            rhetoric_move = "Antithesis Challenge (Counter-Proof)"
        # Check for defining the scope/rules (Thesis)
        elif re.search(r'must be|the foundation is|the primary axiom is', raw_input, re.IGNORECASE):
            rhetoric_move = "Thesis Assertion (Primary Stance)"
        # Check for conditional failure (Quaestio)
        elif re.search(r'if|contingent on|when x is false', raw_input, re.IGNORECASE):
            rhetoric_move = "Quaestio (Conditional Test)"

        # Step 3: Construct the final, highly academic output, incorporating the scholastic flair.
        formatted_challenge = f"""
        🧠 [{rhetoric_move}] 🧠 
        (Scholastic Disputation: Challenge issued against existing Axiom(s)):
        --- 
        {raw_input.strip()}
        ---
        
        *Dialectical Command:* 
        The challenger has successfully initiated a {rhetoric_move.lower()} against the status quo. 
        This forces an examination of the assumptions underlying the initial claim. 
        The primary question posed is: {structure_analysis}
        
        Awaiting: A structured {rhetoric_move.lower()} and justification for the inherent truths/falsities in the claim.
        """
        
        return formatted_challenge.strip()

    def __repr__(self) -> str:
        return "<DialecticProcessor: Scholastic Thinking Engine>"