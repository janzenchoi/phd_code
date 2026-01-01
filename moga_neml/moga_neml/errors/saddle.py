"""
 Title:         The saddle objective function
 Description:   The objective function for minimising the vertical values of
                stationary points between two curves;
                Works well only with periodic data (e.g., cyclic data)
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.errors.__error__ import __Error__
import math, numpy as np

# The Saddle class
class Error(__Error__):
    
    def initialise(self, tolerance:float=10.0):
        """
        Runs at the start, once

        Parameters:
        * `tolerance`: Tolerance for grouping similar y values together
        """
        self.enforce_data_type("cyclic")
        self.tolerance   = tolerance
        x_list           = self.get_x_data()
        y_list           = self.get_y_data()
        exp_dy_dx        = np.gradient(y_list, x_list)
        sp_indexes       = np.where(np.diff(np.sign(exp_dy_dx)))[0]
        self.exp_sp_list = group_sp(np.array(y_list)[sp_indexes], tolerance)
        self.exp_sp_list = remove_zero_sp(self.exp_sp_list, tolerance)
        self.avg_abs_sp  = np.average([abs(sp) for sp in self.exp_sp_list])
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get the predicted stationary points
        x_label     = self.get_x_label()
        y_label     = self.get_y_label()
        prd_dy_dx   = np.gradient(prd_data[y_label], prd_data[x_label])
        sp_indexes  = np.where(np.diff(np.sign(prd_dy_dx)))[0]
        prd_sp_list = group_sp(np.array(prd_data[y_label])[sp_indexes], self.tolerance)

        # Calculate the discrepancies between the stationary points
        discrepancy_list = []
        for i in range(min(len(self.exp_sp_list), len(prd_sp_list))):
            discrepancy = math.pow(self.exp_sp_list[i] - prd_sp_list[i], 2)
            discrepancy_list.append(discrepancy)
        return math.sqrt(np.average(discrepancy_list)) / self.avg_abs_sp

def group_sp(y_list:list, tolerance:float):
    """
    Groups the stationary points together

    Parameters:
    * `y_list`:    The list of values being grouped
    * `tolerance`: The tolerance used for the grouping
    
    Returns the grouped stationary points
    """
    sp_list = []
    curr_group = [y_list[0]]
    for y in y_list[1:]:
        if abs(y - curr_group[-1]) < tolerance:
            curr_group.append(y)
        else:
            sp_list.append(np.average(curr_group))
            curr_group = [y]
    sp_list.append(np.average(curr_group))
    return sp_list

def remove_zero_sp(y_list:list, tolerance:float):
    """
    Removes stationary points close to 0

    Parameters:
    * `y_list`:    The list of values being processed
    * `tolerance`: The tolerance used for the removal
    
    Returns the non-close-to-zero stationary points
    """
    y_list = [y for y in y_list if abs(y) > tolerance]
    return y_list
