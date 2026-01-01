"""
 Title:         The Visco-Plastic Chaboche Linear Isotropic Hardening Model
 Description:   Visco-plastic Chaboche with a linearly isotropic hardening yield surface
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.models.__model__ import __Model__
from neml import elasticity, surfaces, hardening, visco_flow, general_flow, models

# The Visco-Plastic Chaboche Linear Isotropic Hardening Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """
        self.add_param("lih_s0",  0.0e0, 1.0e3) # isotropic hardening initial yield stress
        self.add_param("lih_k",   0.0e0, 1.0e4) # isotropic hardening slope
        self.add_param("vih_n",   0.0e0, 1.0e2) # ViscoFlowRule
        self.add_param("vih_eta", 0.0e0, 1.0e4) # ViscoFlowRule
        self.add_param("c_gs1",   0.0e0, 1.0e4) # Chaboche
        self.add_param("c_gs2",   0.0e0, 1.0e2) # Chaboche
        self.add_param("c_cs1",   0.0e0, 1.0e6) # Chaboche
        self.add_param("c_cs2",   0.0e0, 1.0e4) # Chaboche
    
    def calibrate_model(self, lih_s0, lih_k, vih_n, vih_eta, c_gs1, c_gs2, c_cs1, c_cs2):
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
        chaboche_model = hardening.Chaboche(lih_rule, [c_cs1, c_cs2], gamma_rule, [0.0, 0.0], [2.0, 2.0])
        fluidity       = visco_flow.ConstantFluidity(vih_eta)
        cf_rule        = visco_flow.ChabocheFlowRule(yield_surface, chaboche_model, fluidity, vih_n)
        flow_rule      = general_flow.TVPFlowRule(elastic_model, cf_rule)
        vpclih_model   = models.GeneralIntegrator(elastic_model, flow_rule)
        return vpclih_model
