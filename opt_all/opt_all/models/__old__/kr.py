"""
 Title:         The Kachanov-Rabotnov Model
 Description:   Simple empirical model
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.models.__model__ import __Model__

# The Kachanov-Rabotnov Class
class Model(__Model__):

    def get_response(self, A:float, n:float, M:float, phi:float, chi:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: ...
        
        Returns the response as a dictionary
        """

        # Get experimental data information
        stress = self.get_data("stress")
        # temperature = self.get_data("temperature")

        # Alter parameters
        A = 10**A
        M = 10**M
        
        # Get time values
        ttf = 1/((phi+1)*M*stress**chi)
        time_list = list(np.linspace(0.1, ttf, 100))

        # Evaluate strains
        get_strain = lambda t : A*stress**n * ((1-(phi+1)*M*stress**chi*t)**((phi+1-n)/(phi+1))-1) / (M*stress**chi*(n-phi-1))
        strain_list = [get_strain(t) for t in time_list]

        # Check if nan
        has_nan = np.isnan(strain_list).any()
        if has_nan:
            return

        # Return
        response_dict = {
            "time":   time_list,
            "strain": strain_list
        }
        return response_dict
