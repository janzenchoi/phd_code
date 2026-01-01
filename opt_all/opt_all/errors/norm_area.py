"""
 Title:         The normalised area objective function
 Description:   The objective function for minimising the normalised vertical areas between two curves;
                Only works well for bijective data
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__
from opt_all.helper.interpolator import Interpolator
import math, numpy as np

# The Area class
class Error(__Error__):
    
    def initialise(self, num_points:int=50, max_value:float=None):
        """
        Runs at the start, once

        Parameters:
        * `num_points`: Number of points to evaluate
        * `max_value`:  Maximum value to evaluate to
        """
        
        # Initialise
        self.num_points   = num_points
        x_list            = self.get_x_data()
        y_list            = self.get_y_data()
        self.interpolator = Interpolator(x_list, y_list, self.num_points)
        self.exp_x_end    = min(x_list[-1], max_value) if max_value != None else x_list[-1]
        
        # Define normaliser
        in_l = min(y_list)
        in_u = max(y_list)
        self.normalise = lambda value_list : [linear_map(value, in_l, in_u, 0, 1) for value in value_list]
        self.norm_avg_y = self.normalise([np.average([abs(y) for y in y_list])])[0]
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get predicted data and normalise
        x_label    = self.get_x_label()
        y_label    = self.get_y_label()
        prd_x_list = np.linspace(prd_data[x_label][0], min(self.exp_x_end, prd_data[x_label][-1]), self.num_points)
        try:
            prd_interpolator = Interpolator(prd_data[x_label], prd_data[y_label], self.num_points)
        except:
            return
        prd_y_list = prd_interpolator.evaluate(prd_x_list)
        prd_y_list = self.normalise(prd_y_list)

        # Get experimental data and normalise
        exp_y_list = self.interpolator.evaluate(prd_x_list)
        exp_y_list = self.normalise(exp_y_list)
        
        # Calculate error
        try:
            area = [math.pow(prd_y_list[i] - exp_y_list[i], 2) for i in range(self.num_points) if prd_x_list[i] <= self.exp_x_end]
            return math.sqrt(np.average(area)) / self.norm_avg_y
        except OverflowError:
            return

def linear_map(value:float, in_l:float, in_u:float, out_l:float, out_u:float) -> float:
    """
    Linearly maps a value

    Parameters:
    * `value`:  The value to be mapped
    * `in_l`:   The lower bound of the input
    * `in_u`:   The upper bound of the input
    * `out_l`:  The lower bound of the output
    * `out_u`:  The upper bound of the output

    Returns the mapped value
    """
    if in_l == in_u or out_l == out_u:
        return value
    factor = (out_u - out_l) / (in_u - in_l)
    return (value - in_l) * factor + out_l
