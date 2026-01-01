"""
 Title:         The Rate-Independent Linear Isotropic Kinematic Hardening Model
 Description:   Rate-independent plasticity algorithm with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import ri_flow, elasticity, surfaces, hardening, models

# The Rate-Independent Linear Isotropic Kinematic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("lih_s0", 0.0e0, 1.0e2) # isotropic hardening initial yield stress
        self.add_param("lih_k",  0.0e0, 1.0e3) # isotropic hardening slope
        self.add_param("lkh_h",  0.0e0, 1.0e3) # kinematic hardening slope
        
    def calibrate_model(self, lih_s0, lih_k, lkh_h):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoKinJ2()
        lih_rule      = hardening.LinearIsotropicHardeningRule(lih_s0, lih_k)
        lkh_rule      = hardening.LinearKinematicHardeningRule(lkh_h)
        ch_rule       = hardening.CombinedHardeningRule(lih_rule, lkh_rule)
        plastic_flow  = ri_flow.RateIndependentAssociativeFlow(yield_surface, ch_rule)
        rilikh_model  = models.SmallStrainRateIndependentPlasticity(elastic_model, plastic_flow)
        return rilikh_model
