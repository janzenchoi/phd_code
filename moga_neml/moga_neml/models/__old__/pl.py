"""
 Title:         The Power Law Model
 Description:   Purely empirical model
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import models, elasticity, surfaces, hardening, ri_flow

# The Elastic Visco Plastic Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        
        # Define parameters
        self.add_param("pl_s0", 0.0e0, 1.0e3)
        self.add_param("pl_A",  0.0e0, 1.0e3)
        self.add_param("pl_n",  0.0e0, 1.0e2)
        
    def calibrate_model(self, pl_s0, pl_A, pl_n):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        surface       = surfaces.IsoJ2()
        iso           = hardening.PowerLawIsotropicHardeningRule(pl_s0, pl_A, pl_n)
        flow          = ri_flow.RateIndependentAssociativeFlow(surface, iso)
        pl_model      = models.SmallStrainRateIndependentPlasticity(elastic_model, flow)
        return pl_model