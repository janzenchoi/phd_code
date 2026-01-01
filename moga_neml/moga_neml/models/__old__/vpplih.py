"""
 Title:         The Visco-Plastic Perzyna Linear Isotropic Hardening Model
 Description:   Visco-plastic Chaboche with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import elasticity, surfaces, hardening, visco_flow, general_flow, models

# The Visco-Plastic Perzyna Linear Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("lih_s0", 0.0e0, 1.0e3) # isotropic hardening initial yield stress
        self.add_param("lih_k",  0.0e0, 1.0e4) # isotropic hardening slope
        self.add_param("pl_n",   0.0e0, 1.0e2) # power law
        self.add_param("pl_eta", 0.0e0, 1.0e4) # power law
    
    def calibrate_model(self, lih_s0, lih_k, pl_n, pl_eta):
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
        g_power       = visco_flow.GPowerLaw(pl_n, pl_eta)
        pf_rule       = visco_flow.PerzynaFlowRule(yield_surface, lih_rule, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, pf_rule)
        vpplih_model  = models.GeneralIntegrator(elastic_model, integrator)
        return vpplih_model
