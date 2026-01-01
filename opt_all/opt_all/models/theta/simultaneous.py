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

    def get_response(self,
        a1:float, b1:float, c1:float, d1:float,
        a2:float, b2:float, c2:float, d2:float,
        a3:float, b3:float, c3:float, d3:float,
        a4:float, b4:float, c4:float, d4:float,
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

        # Define theta projection model
        get_t = lambda a, b, c, d : np.exp(a + b*stress + c*temperature + d*stress*temperature)
        t1 = get_t(a1, b1, c1, d1)
        t2 = get_t(a2, b2, c2, d2)
        t3 = get_t(a3, b3, c3, d3)
        t4 = get_t(a4, b4, c4, d4)
        get_strain = lambda time : t1 * (1 - np.exp(-t2*time)) + t3 * (np.exp(t4*time) - 1)

        # Check theta parameters
        for ti in [t1, t2, t3, t4]:
            if np.isnan(ti) or np.isinf(ti) or ti == 0:
                return

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
