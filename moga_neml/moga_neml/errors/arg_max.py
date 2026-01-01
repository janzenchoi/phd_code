"""
 Title:         The arg_max objective function
 Description:   The objective function for minimising the discrepancies between the
                x value corresponding to the maximum y values of two curves
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
        y_list = self.get_y_data()
        self.exp_arg_max = find_arg_max(x_list, y_list)
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        x_list = list(prd_data[x_label])
        y_list = list(prd_data[y_label])
        prd_arg_max = find_arg_max(x_list, y_list)
        return abs(self.exp_arg_max - prd_arg_max) / self.exp_arg_max

def find_arg_max(x_list:list, y_list:list):
    """
    Finds the x value corresponding to the maximum y value

    Parameters:
    * `x_list`: The list of x values
    * `y_list`: The list of y values
    
    Returns the x value
    """
    max_y_index = y_list.index(max(y_list))
    arg_max = x_list[max_y_index]
    return arg_max
