"""
 Title:         The Elastic Viscoplastic Model
 Description:   Incorporates elasto-viscoplasticity
 Author:        Janzen Choi

"""

# Libraries
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow
from opt_all.models.__model__ import __Model__
from opt_all.helper.neml_driver import run_driver

# The Elastic Visco Plastic Class
class Model(__Model__):

    def get_response(self, evp_s0:float, evp_R:float, evp_d:float, evp_n:float,
                        evp_eta:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `evp_s0`:  Elastic-Viscoplastic Parameter
        * `evp_R`:   Elastic-Viscoplastic Parameter
        * `evp_d`:   Elastic-Viscoplastic Parameter
        * `evp_n`:   Elastic-Viscoplastic Parameter
        * `evp_eta`: Elastic-Viscoplastic Parameter
        
        Returns the response as a dictionary
        """

        # Calibrates the model
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
        calib_model   = models.GeneralIntegrator(elastic_model, integrator)

        # Run the driver and return
        model_response = run_driver(self.get_exp_data(), calib_model)
        if model_response == None:
            return None
        return {
            "strain": list(model_response["strain"]),
            "stress": list(model_response["stress"])
        }
