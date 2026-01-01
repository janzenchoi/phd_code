"""
 Title:         The dummy objective function
 Description:   The objective function that just returns 0
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__

# The Dummy class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once; doesn't do anything though
        """
        pass

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns 0, always
        """
        return 0
