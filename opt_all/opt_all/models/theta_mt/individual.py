"""
 Title:         Theta model
 Description:   Theta projection model for single temperature and stresses;
                Follows Evans (1992)
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Theta Projection Model Class
class Model(__Model__):

    def get_response(self, t1:float, t2:float, t3:float, t4:float, t5:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Scale parameters
        t1 = 10**t1
        t2 = 10**t2
        t3 = 10**t3
        t4 = 10**t4
        t5 = 10**t5

        # Evaluate model
        get_strain = lambda time : t1 * (1 - np.exp(-t2*time)) + t3 * (np.exp(t4*time) - 1) + t5*time
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
