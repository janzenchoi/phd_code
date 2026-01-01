"""
 Title:         LCSP model
 Description:   LCSP model for single temperature and stresses
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The LCSP Model Class
class Model(__Model__):

    def get_response(self, phi_1:float, phi_2:float, phi_3:float, phi_4:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Scale parameters
        # phi_1 = 10**phi_1
        # phi_2 = 10**phi_2
        # phi_3 = 10**phi_3
        # phi_4 = 10**phi_4

        # Evaluate model
        get_strain = lambda time : (phi_1*(1+phi_2)*time)**(1/(1+phi_2)) + (phi_3*(1-phi_4)*time)**(1/(1-phi_4))
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
