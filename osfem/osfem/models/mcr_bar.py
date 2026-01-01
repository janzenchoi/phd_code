"""
 Title:         MCR BAR
 Description:   Barnes' model 
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
        self.add_param("a", r"$A_{GA}$",     0, 1e3)
        self.add_param("b", r"$\beta_{GA}$", 0, 1e1)
        self.add_param("n", r"$n_{GA}$",     1, 1e1)
        self.add_param("q", r"$Q_{GA}$",     0, 1e3)
    
    def evaluate(self, a, b, n, q) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        mcr = a*np.sinh(b*s)**n*np.exp(-q/8.314/t)
        return mcr