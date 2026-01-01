"""
 Title:         The Visco-Plastic Perzyna Voce Isotropic Hardening Model
 Description:   Visco-plastic Chaboche with a voce isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import elasticity, surfaces, hardening, visco_flow, general_flow, models

# The Visco-Plastic Perzyna Voce Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("lih_s0", 0.0e0, 1.0e3) # isotropic hardening initial yield stress
        self.add_param("lih_R",  0.0e0, 1.0e3) # isotropic hardening slope
        self.add_param("lih_d",  0.0e0, 1.0e2) # kinematic hardening slope
        self.add_param("pl_n",   0.0e0, 1.0e2) # power law
        self.add_param("pl_eta", 0.0e0, 1.0e4) # power law
    
    def calibrate_model(self, lih_s0, lih_R, lih_d, pl_n, pl_eta):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        lih_rule      = hardening.VoceIsotropicHardeningRule(lih_s0, lih_R, lih_d)
        g_power       = visco_flow.GPowerLaw(pl_n, pl_eta)
        pf_rule       = visco_flow.PerzynaFlowRule(yield_surface, lih_rule, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, pf_rule)
        vppvih_model  = models.GeneralIntegrator(elastic_model, integrator)
        return vppvih_model
