class UserProfile:
    def __init__(self, age: int, gender: str, race: str, city: str):
        """
        Initialize a UserProfile object.

        Args:
            age (int): The age of the user.
            gender (str): The gender of the user.
            race (str): The race of the user.
            city (str): The city where the user resides.
        """
        self.age = age
        self.gender = gender
        self.race = race
        self.city = city
    
    #demographics (copy from above)\
    #self defined
    #other defined

    def to_dict(self) -> dict:
        """
        Convert the user profile to a dictionary.

        Returns:
            dict: The user profile as a dictionary.
        """
        return {
            "Age": self.age,
            "Gender": self.gender,
            "Race": self.race,
            "City": self.city,
        }
