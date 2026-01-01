"""
 Title:         TTF LLM
 Description:   Logarithmic Larson-Miller
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
        # self.add_param("c", r"$c_{MG}$", 0, 1e3)
        self.add_param("c", r"$c_{MG}$", 0, 50)
        self.add_param("m", r"$m_{MG}$", 0, 1)
    
    def evaluate(self, c, m) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        mcr = self.get_field("mcr")
        ttf = (c/mcr)**m
        return ttf
