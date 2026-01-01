"""
 Title:         The max objective function
 Description:   The objective function for minimising the maximum x magnitude of two curves
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# The maximum value class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        x_list = self.get_x_data()
        self.x_max = abs(max(x_list))
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        return abs(self.x_max - max(prd_data[x_label])) / self.x_max
