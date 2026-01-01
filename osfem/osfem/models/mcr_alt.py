"""
 Title:         MCR ALT
 Description:   Altenbach
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
        [1644.1, 0.082423, 6.779, 5.4474] 3%, 20%
        """
        self.add_param("a", r"$A_{AA}$", 0, 1e6)
        self.add_param("b", r"$B_{AA}$", 0, 10)
        self.add_param("n", r"$n_{AA}$", 1, 10)
        self.add_param("q", r"$Q_{AA}$", 0, 1e3)

    def evaluate(self, a, b, n, q) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        mcr = a*s*(1 + (b*s)**n)*np.exp(-q/8.314/t)
        return mcr