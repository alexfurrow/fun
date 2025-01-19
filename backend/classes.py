class initial_text:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.ai_response = None

class Prompt:
    def __init__(self, orientation: str, style: None, author_to_emulate: None, user_profile: None):
        self.orientation = orientation
        self.author_to_emulate = author_to_emulate
        self.style = style
        self.user_profile = user_profile

    def system_prompt(self, orientation: str,):
        if orientation == 'refinement':
            system_prompt = """
                Your goal is to reorganize a user's input and transform it into an organized document that follows the following criteria. \
                1. Restate the user's query in full sentence with proper grammar. Reorganize the query into paragraphs, if necessary, and make the paragraphs self consistent with themes. 
                2. Secondly, identify a timeline to the events of the day.
                3. Maintain the user's voice. Include phrases that they used.     
                Your response must be in JSON format.
                """
        if orientation == 'story_1':
            system_prompt = """
                Refine the user's query in concise language. Parse out their query into . Use the "but/therefore" framework.

                But/therefore framework:
                    Every beat in the story begins with a "but" or a "therefore", except for the first beat in the story. For instance, "one upon a time, there was a king in a castle. BUT the king was sick and THEREFORE all eyes went to his successor. HOWEVER, the king had no sons and no family whatsoever. THEREFORE, they began a search among the greatest knights of the land. THEREFORE, the kings men went out into the kingdom to find the greatest leader.
                    This is a framework that Matt Stone and Trey Parker have articulated and espoused, so  you may reference any information that they have brought up with regards to the BUT/therefore framework.

                For instance: 
                    User Query: "yeah, so i had a great day today. I hadn't eaten well the day before, including a few too many pieces of bread. I wonder if I have a gluten allergy, because it really made me feel bad. Or maybe it was the processed food."
                    Refined
            """

        if orientation == 'poem':
            """ 
            You are a storied and world reknown poet. Your efforts will cause waves of great joy in society for each poem you release. You take the thoughts of the people of the world and turn it into beautiful, sophiticated, and simple poetry.
            """
            
        return(system_prompt)

    def generate_prompt(self, orientation: str, user_input: str) -> str:
        if orientation == 'refinement':
            
            return(
                f"""
                reference the user_input, f{user_input}
                """
                # Example 1:
                # Example 2:
                # Example 3:  
            )
        
        if orientation == 'poem':
            profile_details = ", ".join([f"{key}: {value}" for key, value in self.user_profile.items()])
            return (
                f"Write a {self.style} in the style of {self.author_to_emulate}."
                f"Consider the user's profile ({profile_details}).\n\n Input: {user_input}"
            ) 