"""
 Title:         TTF DSM
 Description:   Dorn-Shepherd Model
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
        self.add_param("d", r"$D_{DS}$", 0, 0.1)
        self.add_param("n", r"$n_{DS}$", 0, 1e1)
        self.add_param("q", r"$Q_{DS}$", 0, 1e3)
    
    def evaluate(self, d, n, q) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        ttf = d*s**(-n)*np.exp(q/8.314/t)
        return ttf
