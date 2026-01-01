"""
 Title:         The Rate-Independent Power Law Isotropic Hardening Model
 Description:   Rate-independent plasticity algorithm with an isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import ri_flow, elasticity, surfaces, hardening, models

# The Rate-Independent Power Law Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("plih_s0", 0.0e0, 1.0e3)
        self.add_param("plih_A",  0.0e0, 1.0e4)
        self.add_param("plih_n",  0.0e0, 1.0e2)
        
    def calibrate_model(self, plih_s0, plih_A, plih_n):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        lih_rule      = hardening.PowerLawIsotropicHardeningRule(plih_s0, plih_A, plih_n)
        plastic_flow  = ri_flow.RateIndependentAssociativeFlow(yield_surface, lih_rule)
        riplih_model  = models.SmallStrainRateIndependentPlasticity(elastic_model, plastic_flow)
        return riplih_model
