"""
 Title:         The end objective function
 Description:   The objective function for minimising the discrepancies between the x end points
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__

# The X End class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        x_list = self.get_x_data()
        self.exp_x_end = x_list[-1]

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        prd_end_value = prd_data[x_label][-1]
        return abs((prd_end_value - self.exp_x_end) / self.exp_x_end)