"""
 Title:         The Rate-Independent Linear Isotropic Hardening Model
 Description:   Rate-independent plasticity algorithm with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import ri_flow, elasticity, surfaces, hardening, models

# The Rate-Independent Linear Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("lih_s0", 0.0e0, 1.0e3) # isotropic hardening initial yield stress
        self.add_param("lih_k",  0.0e0, 1.0e4) # isotropic hardening slope
        
    def calibrate_model(self, lih_s0, lih_k):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        lih_rule      = hardening.LinearIsotropicHardeningRule(lih_s0, lih_k)
        plastic_flow  = ri_flow.RateIndependentAssociativeFlow(yield_surface, lih_rule)
        rilih_model   = models.SmallStrainRateIndependentPlasticity(elastic_model, plastic_flow)
        return rilih_model
