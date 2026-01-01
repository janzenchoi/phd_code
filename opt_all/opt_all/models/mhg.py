"""
 Title:         MHG model
 Description:   MHG model for multiple temperature and stresses;
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Theta Projection Model Class
class Model(__Model__):

    def get_response(self,
        a0:float, a1:float, a2:float, c:float
    ) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Get data
        stress = self.get_data("stress")
        temperature = self.get_data("temperature")
        time_list = self.get_data("time")

        # Define model
        get_f = lambda time : (np.log(time)-c)/temperature
        get_strain = lambda time : np.exp((get_f(time) - a0 - a1*np.log(stress**2))/a2)**(1/3)

        # Evaluate model
        time_list = list(np.linspace(min(time_list), max(time_list), 100))
        strain_list = [get_strain(time) for time in time_list]
        strain_array = np.array(strain_list)
        if np.any(np.isnan(strain_array)) or np.any(np.isinf(strain_array)):
            return

        # Create response dictionary and return
        response_dict = {
            "time":   time_list,
            "strain": strain_list
        }
        return response_dict
