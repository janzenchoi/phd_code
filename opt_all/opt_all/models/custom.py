"""
 Title:         Primary creep model
 Description:   Primary equations
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Primary Creep Class
class Model(__Model__):

    def get_response(self, p_A:float, p_Q:float, p_n:float, p_m:float, p_C:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Get data
        stress = self.get_data("stress")
        temperature = self.get_data("temperature")
        min_time = min(self.get_data("time"))

        # Prepare parameters
        p_A = 10**p_A
        p_Q = 10**p_Q

        # Define equations
        arrhenius = p_A * stress**p_n * np.exp(-p_Q/8.3145/temperature) # miller-norton
        ttf = (p_C / arrhenius / p_m) ** (1/p_m)
        # accelerator = lambda time : (1 - time/ttf)**-p_r
        get_strain = lambda time : arrhenius * time**p_m

        # Create time list
        time_list = list(np.linspace(min_time, ttf, 100))
        strain_list = [get_strain(time) for time in time_list]

        # Create response dictionary and return
        response_dict = {
            "time":   time_list,
            "strain": strain_list
        }
        return response_dict
