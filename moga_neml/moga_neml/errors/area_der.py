"""
 Title:         The derivative area objective function
 Description:   The objective function for minimising the vertical areas between
                the derivatives of two curves
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
from moga_neml.errors.__error__ import __Error__
from moga_neml.helper.data import get_thinned_list
from moga_neml.helper.derivative import differentiate_curve
from moga_neml.helper.interpolator import Interpolator

# Constants
NUM_POINTS = 50

# The Derivative Area class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        x_list = self.get_x_data()
        y_list = self.get_y_data()
        self.interpolator = Interpolator(x_list, y_list, NUM_POINTS)
        self.interpolator.differentiate()
        self.exp_x_end = x_list[-1]
        self.avg_abs_dy = np.average([abs(y) for y in self.interpolator.evaluate(x_list)])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        prd_data[x_label] = get_thinned_list(prd_data[x_label], NUM_POINTS)
        prd_data[y_label] = get_thinned_list(prd_data[y_label], NUM_POINTS)
        prd_data = differentiate_curve(prd_data, x_label, y_label)
        exp_dy_list = self.interpolator.evaluate(prd_data[x_label])
        area = [math.pow(prd_data[y_label][i] - exp_dy_list[i], 2) for i in range(len(prd_data[y_label])) if prd_data[x_label][i] <= self.exp_x_end]
        return math.sqrt(np.average(area)) / self.avg_abs_dy
