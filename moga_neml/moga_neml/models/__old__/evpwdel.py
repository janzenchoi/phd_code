"""
 Title:         The Elastic Viscoplastic Work Damage Model with exponential-linear function for work damage
 Description:   Incorporates elasto-viscoplasticity and work damage
 Author:        Janzen Choi

"""

# Libraries
import numpy as np, math
from moga_neml.models.__model__ import __Model__
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow, damage, interpolate

# Constants
WORK_RATE_BOUNDS = (-20, 5) # in powers of 10

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
        
        # Critical work parameters
        self.add_param("wd_a", 0.0e0, 1.0e5)
        self.add_param("wd_b", 0.0e0, 1.0e4)
        self.add_param("wd_c", 0.0e0, 1.0e5)

        # Exponent parameters
        self.add_param("wd_n0", 1.0e0, 2.0e1)
        self.add_param("wd_n1", 1.0e0, 2.0e1)

    def calibrate_model(self, evp_s0, evp_R, evp_d, evp_n, evp_eta, wd_a, wd_b, wd_c, wd_n0, wd_n1):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """

        # If tensile shelf is not higher than creep shelf, then bad parameters
        if 0 in [wd_a, wd_b, wd_c] or wd_c/wd_a/wd_b < 0 or wd_c >= wd_a*wd_b:
            return
        
        # Define EVP model
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
        evp_model     = models.GeneralIntegrator(elastic_model, integrator, verbose=False)
        
        # Get interpolation data
        wr_list = get_wr_list(wd_a, wd_b, wd_c)
        wc_list = [get_wc(wr, wd_a, wd_b, wd_c) for wr in wr_list]
        n_list  = [get_n(wr, wd_n0, wd_n1) for wr in wr_list]
        wr_list = [math.pow(10, wr) for wr in wr_list]
        
        # Get interpolators
        wd_wc = interpolate.PiecewiseSemiLogXLinearInterpolate(wr_list, wc_list)
        wd_n = interpolate.PiecewiseSemiLogXLinearInterpolate(wr_list, n_list)
        
        # Define work damage model and return
        wd_model = damage.WorkDamage(elastic_model, wd_wc, wd_n, log=False, eps=1e-40, work_scale=1e5)
        evpwd_model = damage.NEMLScalarDamagedModel_sd(elastic_model, evp_model, wd_model, verbose=False)
        return evpwd_model

def get_intercept(a:float, b:float, c:float) -> float:
    return 1/b*math.log(c/a/b)

def get_wr_list(a:float, b:float, c:float) -> list:
    wr_0, wr_2 = WORK_RATE_BOUNDS
    wr_1 = get_intercept(a, b, c)
    wr_list = list(np.linspace(wr_0, wr_1, 16)) + list(np.linspace(wr_1, wr_2, 16))
    return wr_list

def get_wc(wr:float, a:float, b:float, c:float) -> float:
    wr_0, wr_2 = WORK_RATE_BOUNDS
    wr_1 = get_intercept(a, b, c)
    if wr_0 < wr and wr <= wr_1:
        return a*math.exp(b*wr)
    elif wr_1 < wr and wr <= wr_2:
        return c*wr + c/b*(1 - math.log(c/a/b))
    else:
        return 0

def get_n(wr:float, n_0:float, n_1:float) -> float:
    return n_0*wr + n_1
