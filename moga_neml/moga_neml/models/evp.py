"""
 Title:         The Elastic Viscoplastic Model
 Description:   Incorporates elasto-viscoplasticity
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow

# The Elastic Visco Plastic Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("evp_s0",  0.0e0, 1.0e3) # 3 (</ 1e2)
        self.add_param("evp_R",   0.0e0, 1.0e3) # 4
        # self.add_param("evp_d",   0.0e0, 1.0e2) # 2
        self.add_param("evp_d",   0.0e0, 1.0e1) # 2
        self.add_param("evp_n",   1.0e0, 1.0e2) # 2
        self.add_param("evp_eta", 0.0e0, 1.0e4) # 5
        
    def calibrate_model(self, evp_s0:float, evp_R:float, evp_d:float, evp_n:float, evp_eta:float):
        """
        Gets the predicted curves

        Parameters:
        * `evp_s0`:  Initial yield stress
        * `evp_R`:   Isotropic hardening stress
        * `evp_d`:   Isotropic hardening rate
        * `evp_n`:   Rate sensitivity
        * `evp_eta`: Viscoplastic fluidity

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
        evp_model     = models.GeneralIntegrator(elastic_model, integrator, verbose=False)
        return evp_model