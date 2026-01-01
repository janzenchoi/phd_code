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
        p11:float, p12:float, p13:float, p14:float,
        p21:float, p22:float, p23:float, p24:float,
        p31:float, p32:float, p33:float, p34:float,
        p41:float, p42:float, p43:float, p44:float,
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
        get_t = lambda p1, p2, p3, p4 : np.exp(p1 + p2*stress + p3*temperature + p4*stress*temperature)
        t1 = get_t(p11, p12, p13, p14)
        t2 = get_t(p21, p22, p23, p24)
        t3 = get_t(p31, p32, p33, p34)
        t4 = get_t(p41, p42, p43, p44)
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
