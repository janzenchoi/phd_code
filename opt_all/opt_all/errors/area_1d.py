"""
 Title:         The area objective function (1D)
 Description:   The objective function for minimising the vertical areas between two curves;
                Assumes experimental and simulated values line up
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__
import math, numpy as np

# The Area class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once

        Parameters:
        * `num_points`: Number of points to evaluate
        * `min_value`:  Minimum value to evaluate to
        * `max_value`:  Maximum value to evaluate to
        """
        x_list = self.get_x_data()
        self.average_x = np.average([abs(x) for x in x_list])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get data
        exp_x_list = self.get_x_data()
        x_label    = self.get_x_label()
        prd_x_list = prd_data[x_label]

        # Calculate error
        try:
            area = [math.pow(prd_x-exp_x, 2) for exp_x, prd_x in zip(exp_x_list, prd_x_list)]
            return math.sqrt(np.average(area)) / self.average_x
        except OverflowError:
            return
