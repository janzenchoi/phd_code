"""
 Title:         The area saddle objective function
 Description:   The objective function for minimising the vertical area of two curves
                by normalising between their stationary points;
                Works well only with periodic data (e.g., cyclic data)
 Author:        Janzen Choi

"""

# Libraries
import math, matplotlib.pyplot as plt, numpy as np
from moga_neml.errors.__error__ import __Error__
from moga_neml.helper.interpolator import Interpolator
from moga_neml.helper.experiment import remove_zero_sp, group_sp

# The Area Saddle class
class Error(__Error__):
    
    def initialise(self, num_points:int=50, tolerance:float=10.0):
        """
        Runs at the start, once

        Parameters:
        * `num_points`: Number of points between saddles to evaluate
        * `tolerance`:  Tolerance for grouping similar x values together
        """
        self.enforce_data_type("cyclic")
        self.num_points = num_points
        self.tolerance = tolerance
        x_list = self.get_x_data()
        y_list = self.get_y_data()
        self.exp_interp_list, _ = get_interp_list(x_list, y_list, num_points, tolerance)
        self.norm_x_list = np.linspace(0, 1, num_points)
        self.avg_abs_y = np.average([abs(y) for y in y_list])
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get interpolators for predicted data
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        prd_interp_list, _ = get_interp_list(prd_data[x_label], prd_data[y_label],
                                          self.num_points, self.tolerance)
        
        # Check if any interpolations fail
        if None in prd_interp_list:
            return

        # Iterate through interpolators and calculate their discrepancies
        discrepancy_list = []
        min_interp = min(len(self.exp_interp_list), len(prd_interp_list))
        for i in range(min_interp):
            exp_y_list = self.exp_interp_list[i].evaluate(self.norm_x_list)
            prd_y_list = prd_interp_list[i].evaluate(self.norm_x_list)
            discrepancy_list += [math.pow(exp_y_list[j] - prd_y_list[j], 2) for j in range(self.num_points)]
        return math.sqrt(np.average(discrepancy_list)) / self.avg_abs_y

def test_interp_list(x_list:list, y_list:list, interp_list:list, raw_x_list_list:list) -> None:
    """
    Plots the results of the interpolator list

    Parameters:
    * `x_list`:          The list of x values
    * `y_list`:          The list of y values
    * `interp_list`:     The list of interpolators
    * `raw_x_list_list`: The list of raw x lists
    """
    plt.plot(x_list, y_list)
    for i in range(len(interp_list)):
        raw_x_list = raw_x_list_list[i]
        norm_x_list = np.linspace(0, 1, raw_x_list)
        interp_y_list = interp_list[i].evaluate(norm_x_list)
        plt.scatter(raw_x_list, interp_y_list)
    plt.savefig("plot.png")

def get_interp_list(x_list:list, y_list:list, num_points:int, tolerance:float) -> tuple:
    """
    Gets a list of interpolators for data between saddle points

    Parameters:
    * `x_list`:     The list of x values
    * `y_list`:     The list of y values
    * `num_points`: The number of points between saddles for interpolating
    * `tolerance`:  The tolerance used for the grouping
    
    Returns the list of interpolators and the corresponding raw list of x values
    """

    # Get intervals for interpolators
    dy_dx_list = np.gradient(y_list, x_list)
    sp_indexes = np.where(np.diff(np.sign(dy_dx_list)))[0]
    sp_x_list = np.array(x_list)[sp_indexes]
    sp_y_list = np.array(y_list)[sp_indexes]
    sp_x_list, sp_y_list = group_sp(sp_x_list, sp_y_list, tolerance)
    sp_x_list, sp_y_list = remove_zero_sp(sp_x_list, sp_y_list, tolerance)
    sp_x_list = [0] + sp_x_list

    # Get list of interpolators
    interp_list = []
    for i in range(len(sp_x_list)-1):
        
        # Get interpolation data
        y_interp_list = [y_list[j] for j in range(len(y_list))
                         if x_list[j] >= sp_x_list[i] and x_list[j] <= sp_x_list[i+1]]
        x_interp_list = np.linspace(0, 1, len(y_interp_list))
        
        # Get interpolator; will fail if there are insufficient data points
        try:
            interp = Interpolator(x_interp_list, y_interp_list)
        except TypeError:
            interp = None
        interp_list.append(interp)
    
    # Return
    raw_x_list_list = [np.linspace(sp_x_list[i], sp_x_list[i+1], num_points) for i in range(len(sp_x_list)-1)]
    return interp_list, raw_x_list_list
