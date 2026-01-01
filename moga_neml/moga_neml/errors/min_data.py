"""
 Title:         The min_data objective function
 Description:   The objective function that throws a big error if there are insufficient points
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# Constants
MIN_DATA = 50

# The MinData class
class Error(__Error__):

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        if len(prd_data[x_label]) < MIN_DATA:
            return
        return 0 # it has sufficient data