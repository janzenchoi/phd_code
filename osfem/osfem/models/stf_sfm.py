"""
 Title:         STF SFM
 Description:   Soares Fracture Model 
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
        self.add_param("a", r"$a_{So}$", -1, 1)
        self.add_param("b", r"$b_{So}$", -1, 1)
        self.add_param("c", r"$c_{So}$", -1, 1)
        self.add_param("d", r"$d_{So}$", -1, 1)
        self.add_param("e", r"$e_{So}$", -1, 1)
    
    def evaluate(self, a, b, c, d, e) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        stf = a + b/t + c*s/t + d*np.log(1/t) + e*s
        return stf
