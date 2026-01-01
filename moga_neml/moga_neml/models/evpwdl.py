"""
 Title:         The Elastic Viscoplastic Work Damage Model with a linear function for work damage
 Description:   Incorporates elasto-viscoplasticity and work damage
 Author:        Janzen Choi

"""

# Libraries
import numpy as np, math
from moga_neml.models.__model__ import __Model__
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow, damage, interpolate

# The Elastic Visco Plastic Work Damage Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """

        # Elastic parameters
        self.add_param("evp_s0",  0.0e0, 1.0e2) # 3 (</ 1e2)
        self.add_param("evp_R",   0.0e0, 1.0e3) # 4
        self.add_param("evp_d",   0.0e0, 1.0e2) # 2
        self.add_param("evp_n",   1.0e0, 1.0e2) # 2
        self.add_param("evp_eta", 0.0e0, 1.0e4) # 5
        
        # Creep damage parameters
        self.add_param("wd_n", 0.0e0, 1.0e2)
        self.add_param("wd_0", 0.0e0, 1.0e3)
        self.add_param("wd_1", 0.0e0, 1.0e3)

    def calibrate_model(self, evp_s0, evp_R, evp_d, evp_n, evp_eta, wd_n, wd_0, wd_1):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        
        # Define EVP model
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
        evp_model     = models.GeneralIntegrator(elastic_model, integrator, verbose=False)
        
        # Prepare the critical points of the linear curve
        x_list = list(np.linspace(-12, 3, 32))
        y_list = [wd_0 * x + wd_1 for x in x_list]
        x_list = [math.pow(10, x) for x in x_list]
        wd_wc = interpolate.PiecewiseSemiLogXLinearInterpolate(x_list, y_list)
        
        # Define work damage model and return
        wd_model = damage.WorkDamage(elastic_model, wd_wc, wd_n, log=False, eps=1e-40, work_scale=1e5)
        evpwd_model = damage.NEMLScalarDamagedModel_sd(elastic_model, evp_model, wd_model, verbose=False)
        return evpwd_model
