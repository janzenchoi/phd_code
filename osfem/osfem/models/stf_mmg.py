"""
 Title:         STF MMG
 Description:   Modified Monkman Grant 
 Author:        Janzen Choi

"""

# Libraries
from osfem.models.__model__ import __Model__

# Model class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("c", r"$c_{Do}$", 0, 1)
        self.add_param("m", r"$m_{Do}$", 0, 2)
    
    def evaluate(self, c, m) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        mcr = self.get_field("mcr")
        ttf = self.get_field("ttf")
        stf = ttf/(c/mcr)**m
        return stf
