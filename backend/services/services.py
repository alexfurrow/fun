from typing import Dict, Optional

class Prompt:
    def __init__(self, 
                 orientation: str, 
                 style: Optional[str] = None, 
                 author_to_emulate: Optional[str] = None, 
                 user_profile: Optional[Dict] = None):
        self.orientation = orientation
        self.author_to_emulate = author_to_emulate
        self.style = style
        self.user_profile = user_profile

    def system_prompt(self, orientation: str) -> str:
        # Your existing system_prompt method
        pass

    def generate_prompt(self, orientation: str, user_input: str) -> str:
        # Your existing generate_prompt method
        pass
