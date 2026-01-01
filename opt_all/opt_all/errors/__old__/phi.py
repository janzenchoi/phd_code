"""
 Title:         The phi objective function
 Description:   The objective function for minimising the discrepancies between the
                linearly mapped start and end points of orientation trajectories
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__
import numpy as np

# The Start-End class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        self.exp_x = self.get_x_data()[-1]
        self.exp_y = self.get_y_data()[-1]
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        gradient = (prd_data[y_label][-1]-prd_data[y_label][0])/(prd_data[x_label][-1]-prd_data[x_label][0])
        prd_y = gradient*(self.exp_x-prd_data[x_label][0]) + prd_data[y_label][0]
        end = abs(get_ae(prd_y, self.exp_y)/self.exp_y)
        return end

def get_ae(value_1:float, value_2:float) -> float:
    """
    Computes the absolute error of two values;
    does so in a cyclic manner between 0 and 2*pi
    
    Parameters:
    * `value_1`: The first value
    * `value_2`: The second value
    
    Returns the absolute error
    """
    abs_1 = abs(value_1 - value_2)
    abs_2 = abs(value_1 - value_2 - 2*np.pi)
    return min(abs_1, abs_2)
