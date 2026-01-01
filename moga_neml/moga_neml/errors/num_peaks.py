"""
 Title:         The n_cycles objective function
 Description:   The objective function for minimising the number of cycles in a periodic curve
 Author:        Janzen Choi

 """

# Libraries
from moga_neml.errors.__error__ import __Error__
from moga_neml.helper.derivative import get_stationary_points

# The Error class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        self.enforce_data_type("cyclic")
        exp_data = self.get_exp_data()
        self.x_label = self.get_x_label()
        self.y_label = self.get_y_label()
        self.exp_num_cycles = get_cycle(exp_data, self.x_label, self.y_label)

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        prd_num_cycles = get_cycle(prd_data, self.x_label, self.y_label)
        return abs(self.exp_num_cycles - prd_num_cycles) / self.exp_num_cycles

def get_cycle(data_dict:dict, x_label:str, y_label:str) -> int:
    """
    Gets the number of cycles

    Parameters:
    * `data_dict`: The data dictionary
    * `x_label`:   The label for the x axis
    * `y_label`:   The label for the y axis
    
    Returns the number of cycles
    """
    return len(get_stationary_points(data_dict, x_label, y_label, 0.2, 0.9))
