"""
 Title:         TTF LLM
 Description:   Logarithmic Larson-Miller
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from osfem.models.__model__ import __Model__

# Model class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("a", r"$a_{LM}$", 0, 1e1)
        self.add_param("b", r"$b_{LM}$", 0, 1e1)
        self.add_param("c", r"$c_{LM}$", 0, 1e2)
        self.add_param("C", r"$C_{LM}$", 0, 1e1)
    
    # def evaluate(self, a, b, c, C) -> float:
    def evaluate(self, a, b, c, C) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        p = -a*np.log(s) - b*s + c
        ttf = np.exp(p/t-C)
        return ttf
