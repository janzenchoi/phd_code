"""
 Title:         Theta model
 Description:   Theta projection model for multiple temperature and stresses;
                Follows Evans (1992)
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Theta Projection Model Class
class Model(__Model__):

    def initialise(self, omega_param:str) -> None:
        """
        Runs at the start, once
        """
        self.omega_param = omega_param

    def get_response(self, a:float, n:float, q:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Get data
        stress_list      = self.get_data("stress")
        temperature_list = self.get_data("temperature")

        # Get omega values
        get_omega = lambda s, t : a*s**n*np.exp(-q/8.314/t)
        omega_list = [get_omega(s, t) for s, t in zip(stress_list, temperature_list)]

        # Create response dictionary and return
        response_dict = {
            "stress": stress_list,
            "temperature": temperature_list,
            self.omega_param: omega_list,
        }
        return response_dict
