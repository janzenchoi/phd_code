"""
 Title:         The area objective function
 Description:   The objective function for minimising the vertical areas between two curves;
                Only works well for bijective data
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__
from opt_all.helper.interpolator import Interpolator
import math, numpy as np

# The Area class
class Error(__Error__):
    
    def initialise(self, num_points:int=50, min_value:float=None, max_value:float=None):
        """
        Runs at the start, once

        Parameters:
        * `num_points`: Number of points to evaluate
        * `min_value`:  Minimum value to evaluate to
        * `max_value`:  Maximum value to evaluate to
        """

        # Initialise interpolator
        self.num_points   = num_points
        x_list            = self.get_x_data()
        y_list            = self.get_y_data()
        self.interpolator = Interpolator(x_list, y_list, len(x_list))
        
        # Define bounds
        self.min_x_value = max(min(x_list), min_value) if min_value != None else min(x_list)
        self.max_x_value = min(max(x_list), max_value) if max_value != None else max(x_list)

        # Define average value
        bounded_x_list = list(np.linspace(self.min_x_value, self.max_x_value, 100))
        bounded_y_list = self.interpolator.evaluate(bounded_x_list)
        self.average_y = np.average([abs(y) for y in bounded_y_list])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get predicted interpolator
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        try:
            prd_interpolator = Interpolator(prd_data[x_label], prd_data[y_label], len(prd_data[x_label]))
        except:
            return
        
        # Determine common region
        min_x_value = max(self.min_x_value, min(prd_data[x_label]))
        max_x_value = min(self.max_x_value, max(prd_data[x_label]))
        common_x_list = list(np.linspace(min_x_value, max_x_value, self.num_points))

        # Get y values
        exp_y_list = self.interpolator.evaluate(common_x_list)
        prd_y_list = prd_interpolator.evaluate(common_x_list)

        # Calculate error
        try:
            area = [math.pow(prd_y-exp_y, 2) for exp_y, prd_y in zip(exp_y_list, prd_y_list)]
            return math.sqrt(np.average(area)) / self.average_y
        except OverflowError:
            return
