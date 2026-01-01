"""
 Title:         The phi objective function
 Description:   The objective function for minimising the discrepancies between the
                gradient of the orientations
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__

# The Start-End class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        x_list = self.get_x_data()
        y_list = self.get_y_data()
        self.exp_gradient = (y_list[-1]-y_list[0])/(x_list[-1]-x_list[0])
        
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        x_label = self.get_x_label()
        y_label = self.get_y_label()
        prd_gradient = (prd_data[y_label][-1]-prd_data[y_label][0])/(prd_data[x_label][-1]-prd_data[x_label][0])
        error = abs((self.exp_gradient-prd_gradient)/self.exp_gradient)
        return error
