"""
 Title:         The norm_area objective function
 Description:   The objective function for minimising the vertical areas between two curves;
                Normalises the x values; Only works well for bijective data
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
from moga_neml.errors.__error__ import __Error__
from moga_neml.helper.interpolator import Interpolator

# The Normalised Area class
class Error(__Error__):
    
    def initialise(self, num_points:int=50):
        """
        Runs at the start, once
        """

        # Get normalised data
        self.num_points = num_points
        x_list          = self.get_x_data()
        y_list          = self.get_y_data()
        exp_interp      = Interpolator(normalise(x_list), y_list, self.num_points)

        # Precalculate values
        self.x_list     = np.linspace(0.0, 1.0, self.num_points)
        self.exp_y_list = exp_interp.evaluate(self.x_list)
        self.avg_abs_y  = np.average([abs(y) for y in self.exp_y_list])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get normalised predicted data
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        prd_interp = Interpolator(normalise(prd_data[x_label]), prd_data[y_label], self.num_points)

        # Calculate error
        prd_y_list = prd_interp.evaluate(self.x_list)
        area = [math.pow(prd_y_list[i] - self.exp_y_list[i], 2) for i in range(self.num_points)]
        return math.sqrt(np.average(area)) / self.avg_abs_y

def normalise(value_list:list) -> list:
    """
    Normalises a list of values to [0, 1]

    Parameters:
    * `value_list`: The list of values

    Returns the normalised list of values
    """
    min_value = min(value_list)
    max_value = max(value_list)
    value_list = [(value - min_value) / (max_value - min_value) for value in value_list]
    return value_list
