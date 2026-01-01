"""
 Title:         The end_more objective function
 Description:   The objective function for making sure that the simulated end value is more than the experimental end value
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# The End More class
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
        return max((self.exp_x_end - prd_end_value) / self.exp_x_end, 0)