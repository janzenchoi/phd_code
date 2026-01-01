"""
 Title:         MCR ARR
 Description:   Arrhenius 
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
        self.add_param("a", r"$A_{NA}$", 0, 1e6)
        self.add_param("n", r"$n_{NA}$", 1, 1e1)
        self.add_param("q", r"$Q_{NA}$", 0, 1e3)
    
    def evaluate(self, a, n, q) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        mcr = a*s**n*np.exp(-q/8.314/t)
        return mcr