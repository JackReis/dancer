# peer_grill/state_manager.py

import os
from datetime import datetime

class ClaimsStateManager:
    """
    Manages the persistent, append-only state of the peer-grill session.
    This class ensures that the log file is treated as an immutable ledger of debate, 
    preventing accidental modification and enforcing log structure.
    
    It is the single source of truth for the knowledge graph formed during the 'grilling'.
    """

    def __init__(self, log_filename: str, max_lines: int = 1000):
        """
        Initializes the state manager for a specific session log.
        
        :param log_filename: The path to the dedicated, append-only log file.
        :param max_lines: The maximum number of lines to retain in the log history.
        """
        self.log_filename = log_filename
        self.max_lines = max_lines
        self._validate_and_initialize_log()

    def _validate_and_initialize_log(self):
        """
        Ensures the log directory exists and checks basic file permissions.
        Makes the file a writeable ledger for the session.
        """
        # Ensure the parent directory structure exists for the session log
        dir_name = os.path.dirname(self.log_filename)
        if dir_name and not os.path.exists(dir_name):
             os.makedirs(dir_name, exist_ok=True)
        
    def dump_claims(self, claims: str, agents: list[str]) -> None:
        """
        Records the initial set of axioms and claims into the ledger.
        This is the starting point: the initial hypothesis space.
        
        :param claims: The raw string of initial claims.
        :param agents: List of agents contributing initially, for attribution.
        """
        header = f"\n\n==================== INITIAL CLAIM DUMP ({datetime.now().isoformat()}) ====================\n"
        header += f"Contributing Agents: {', '.join(agents)}\n"
        header += f"RAW CLAIMS:\n{claims}\n"
        header += "--------------------------------------------------------------------------------------------\n"
        
        self.append_to_log(header + "\n")
        
    def append_to_log(self, content: str) -> None:
        """
        Appends content reliably to the log file, effectively achieving append-only write.
        Handles potential log trimming if the ledger exceeds its memory capacity.
        
        :param content: The content string to append.
        """
        try:
            # The 'a' mode ensures atomic appending, critical for ledger integrity.
            with open(self.log_filename, 'a', encoding='utf-8') as f:
                # Write the content, followed by an intentional separator for structural integrity
                f.write(content.strip() + "\n[--- END OF ROUND ENTRY ---]\n")
            
            # Immediately check and enforce the history limit after writing
            self._trim_log_if_needed()

        except IOError as e:
            raise IOError(f"CRITICAL FAILURE: Failed to write to the immutable log file {self.log_filename}. Check permissions. Error: {e}")
            
    def _trim_log_if_needed(self) -> None:
        """
        A memory management function that prunes the oldest entries if the log
        exceeds the defined line count, preserving the most recent, active debate cycle.
        """
        # This mechanism respects the 'continuous debate' nature by pruning old, cold context.
        try:
            with open(self.log_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) > self.max_lines:
                # Keep the N most recent lines (the current memory span)
                new_content = "".join(lines[-(self.max_lines):])
                
                print(f"[INFO: STATE MANAGER] Log file exceeded {self.max_lines} lines. Trimming history to maintain focus on recent debate.")
                
                # Overwrite the existing file gracefully
                with open(self.log_filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        except FileNotFoundError:
            # This is expected if the file was just created.
            pass 

    def get_history(self) -> str:
        """
        Retrieves the current, full content of the log file for human review or analysis.
        """
        if not os.path.exists(self.log_filename):
            return "Error: State log file does not exist. Session not initialized."
        
        return open(self.log_filename, 'r', encoding='utf-8').read()

    def __repr__(self) -> str:
        return f"<ClaimsStateManager: {self.log_filename}>"