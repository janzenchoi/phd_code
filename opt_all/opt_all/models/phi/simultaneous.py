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
        a1:float, a2:float, a3:float, a4:float,
        n1:float, n2:float, n3:float, n4:float,
        q1:float, q2:float, q3:float, q4:float,
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
        get_phi = lambda a, n, q : a*stress**n*np.exp(-q/8.314/temperature)
        phi_1 = get_phi(a1, n1, q1)
        phi_2 = get_phi(a2, n2, q2)
        phi_3 = get_phi(a3, n3, q3)
        phi_4 = get_phi(a4, n4, q4)
        get_strain = lambda time : (phi_1*(1+phi_2)*time)**(1/(1+phi_2)) + (phi_3*(1-phi_4)*time)**(1/(1-phi_4))

        # Evaluate model
        time_list = list(np.linspace(0, 1, 100))
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
