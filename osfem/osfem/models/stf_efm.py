"""
 Title:         STF ELM
 Description:   Evan's Linear Model 
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
        self.add_param("a", r"$a_{Ev}$", -1, 1)
        self.add_param("b", r"$b_{Ev}$", -1, 1)
        self.add_param("c", r"$c_{Ev}$", -1, 1)
        self.add_param("d", r"$d_{Ev}$", -1, 1)
    
    def evaluate(self, a, b, c, d) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        s = self.get_field("stress")
        t = self.get_field("temperature")
        stf = a + b*s + c*t + d*s*t
        return stf
