"""
 Title:         Theta model
 Description:   Theta projection model for multiple temperature and stresses;
                Follows Evans (1992)
 Author:        Janzen Choi

"""

# Libraries
from opt_all.models.__model__ import __Model__

# The Theta Projection Model Class
class Model(__Model__):

    def initialise(self, theta_param:str) -> None:
        """
        Runs at the start, once
        """
        self.theta_param = theta_param

    def get_response(self, a:float, b:float, c:float, d:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `...`: Parameters
        
        Returns the response as a dictionary
        """

        # Get data
        stress_list      = self.get_data("stress")
        temperature_list = self.get_data("temperature")

        # Get theta values
        get_theta = lambda s, t : a + b*s + c*t + d*s*t
        theta_list = [get_theta(s, t) for s, t in zip(stress_list, temperature_list)]
        # theta_list = [theta*np.log10(2.71828) for theta in theta_list]

        # Create response dictionary and return
        response_dict = {
            "stress": stress_list,
            "temperature": temperature_list,
            self.theta_param: theta_list,
        }
        return response_dict
