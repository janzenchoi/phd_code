"""
 Title:         The Rate-Independent Voce Isotropic Hardening Model
 Description:   Rate-independent plasticity algorithm with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import ri_flow, elasticity, surfaces, hardening, models

# The Rate-Independent Voce Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("vih_s0", 0.0e0, 1.0e3) # VoceIsotropicHardeningRule
        self.add_param("vih_R",  0.0e0, 1.0e3) # VoceIsotropicHardeningRule
        self.add_param("vih_d",  0.0e0, 1.0e2) # VoceIsotropicHardeningRule

    def calibrate_model(self, vih_s0, vih_R, vih_d):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        vih_rule      = hardening.VoceIsotropicHardeningRule(vih_s0, vih_R, vih_d)
        plastic_flow  = ri_flow.RateIndependentAssociativeFlow(yield_surface, vih_rule)
        rivih_model   = models.SmallStrainRateIndependentPlasticity(elastic_model, plastic_flow)
        return rivih_model
