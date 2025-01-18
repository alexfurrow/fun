class initial_text:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.ai_response = None

class Prompt:
    def __init__(self, style: str, author_to_emulate: str, user_profile: dict):
        self.author_to_emulate = author_to_emulate
        self.style = style
        self.user_profile = user_profile
    
    def system_prompt(self):
        system_prompt = "You are a sage and storied writer who has amassed knoweldge across all human written and oral history. You will take the sacred information shared to you and form them into stories and poems. Your responses must be in JSON format"
        return(system_prompt)

    def generate_prompt(self, user_input: str) -> str:
        profile_details = ", ".join([f"{key}: {value}" for key, value in self.user_profile.items()])
        return (
            f"Write a {self.style} in the style of {self.author_to_emulate}."
            f"Consider the user's profile ({profile_details}).\n\n Input: {user_input}"
        ) 