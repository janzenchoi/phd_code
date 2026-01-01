"""
 Title:         Omega model
 Description:   Omega model for single temperature and stresses
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Omega Model Class
class Model(__Model__):

    def get_response(self, o1:float, o2:float, o3:float, o4:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Scale parameters
        # o1 = 10**o1
        # o2 = 10**o2
        # o3 = 10**o3
        # o4 = 10**o4

        # Evaluate model
        get_strain = lambda time : np.log(o1*o2*time+1)/o2 - np.log(-o3*o4*time+1)/o4
        time_list = list(np.linspace(0, 1, 100))
        strain_list = [get_strain(time) for time in time_list]
        
        # Check data
        strain_array = np.array(strain_list)
        if np.any(np.isnan(strain_array)) or np.any(np.isinf(strain_array)):
            return

        # Create response dictionary and return
        response_dict = {
            "time":   time_list,
            "strain": strain_list
        }
        return response_dict
