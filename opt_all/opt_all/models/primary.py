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

    def get_response(self, p_A:float, p_Q:float, p_n:float, p_m:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        itf.bind_param("p_A", -1e2, 0e0)
        itf.bind_param("p_Q",  0e0, 1e1)
        itf.bind_param("p_n",  0e0, 1e1)
        itf.bind_param("p_m",  0e0, 1e0)

        Returns the response as a dictionary
        """

        # Get data
        stress = self.get_data("stress")
        temperature = self.get_data("temperature")
        min_time = min(self.get_data("time"))
        max_time = max(self.get_data("time"))

        # Prepare parameters
        p_A = 10**p_A
        p_Q = 10**p_Q

        # Define equations
        arrhenius = p_A * stress**p_n * np.exp(-p_Q/8.3145/temperature) # miller-norton
        get_strain = lambda time : arrhenius * time**p_m

        # Create time list
        time_list = list(np.linspace(min_time, max_time, 100))
        strain_list = [get_strain(time) for time in time_list]

        # Create response dictionary and return
        response_dict = {
            "time":   time_list,
            "strain": strain_list
        }
        return response_dict
