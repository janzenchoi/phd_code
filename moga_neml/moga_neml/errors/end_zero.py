"""
 Title:         The end_value objective function
 Description:   The objective function for minimising the x end point
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# The X End class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        x_list = self.get_x_data()
        self.max_x = max(x_list)

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        prd_x_end = prd_data[x_label][-1]
        return abs(prd_x_end / self.max_x)