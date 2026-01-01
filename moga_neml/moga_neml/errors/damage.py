"""
 Title:         The n_cycles objective function
 Description:   The objective function for optimising damage to be closer to 1
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# The Error class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        self.model = self.get_model()

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        damage_history = prd_data["history"][-1]
        damage = self.model.get_last_calibrated_model().get_damage(damage_history)
        return abs(1 - damage)
