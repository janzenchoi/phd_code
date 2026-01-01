"""
 Title:         The Rate-Independent Chaboche Linear Isotropic Hardening Model
 Description:   Rate-Independent Chaboche with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import elasticity, surfaces, hardening, models, ri_flow

# The Rate-Independent Chaboche Linear Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("lih_s0", 0.0e0, 1.0e3) # isotropic hardening initial yield stress
        self.add_param("lih_k",  0.0e0, 1.0e4) # isotropic hardening slope
        self.add_param("c_gs1",  0.0e0, 1.0e4) # Chaboche
        self.add_param("c_gs2",  0.0e0, 1.0e2) # Chaboche
        self.add_param("c_cs1",  0.0e0, 1.0e6) # Chaboche
        self.add_param("c_cs2",  0.0e0, 1.0e4) # Chaboche
    
    def calibrate_model(self, lih_s0, lih_k, c_gs1, c_gs2, c_cs1, c_cs2):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model  = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                                self.get_data("poissons"), "poissons")
        yield_surface  = surfaces.IsoKinJ2()
        lih_rule       = hardening.LinearIsotropicHardeningRule(lih_s0, lih_k)
        gamma_rule     = [hardening.ConstantGamma(g) for g in [c_gs1, c_gs2]]
        chaboche_model = hardening.Chaboche(lih_rule, [c_cs1, c_cs2], gamma_rule, [0.0, 0.0], [1.0, 1.0])
        plastic_flow   = ri_flow.RateIndependentNonAssociativeHardening(yield_surface, chaboche_model)
        riclih_model   = models.SmallStrainRateIndependentPlasticity(elastic_model, plastic_flow)
        return riclih_model
