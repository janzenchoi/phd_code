"""
 Title:         Isotropic Elasticity in NEML2
 Description:   For creating the material file;
                Based on moose/modules/solid_mechanics/test/tests/neml2/models/elasticity.i
 Author:        Janzen Choi

"""

# Libraries
from moose_sim.materials.__material__ import __Material__

# Format for defining materials
MATERIAL_FORMAT = """
# ==================================================
# Define Solver
# ==================================================

[Solvers]
  [newton]
    type = NewtonWithLineSearch
    max_linesearch_iterations = 5
  []
[]

# ==================================================
# Define Auxiliary Tensors
# ==================================================

[Tensors]
  [./lattice_a]
    type = Scalar
    values = '{lattice_a}'
  [../]
  [./slip_dir]
    type = FillMillerIndex
    values = '{slip_dir}'
  [../]
  [./slip_plane]
    type = FillMillerIndex
    values = '{slip_plane}'
  [../]
[]

# ==================================================
# Define Crystal Structure
# ==================================================

[Data]
  [./crystal_geometry]
    type = CubicCrystal
    lattice_parameter = "lattice_a"
    slip_directions = "slip_dir"
    slip_planes = "slip_plane"
  [../]
[]

# ==================================================
# Define Model
# ==================================================

[Models]
  [./euler_rodrigues]
    type = RotationMatrix
    from = 'state/orientation'
    to = 'state/orientation_matrix'
  [../]
  [./elasticity]
    type = LinearIsotropicElasticity
    youngs_modulus = {youngs}
    poisson_ratio = {poissons}
    strain = "state/elastic_strain"
    stress = "state/internal/cauchy_stress"
  [../]
  [./resolved_shear]
    type = ResolvedShear
  [../]
  [./elastic_stretch]
    type = ElasticStrainRate
  [../]
  [./plastic_spin]
    type = PlasticVorticity
  [../]
  [./plastic_deformation_rate]
    type = PlasticDeformationRate
  [../]
  [./orientation_rate]
    type = OrientationRate
  [../]
  [./sum_slip_rates]
    type = SumSlipRates
  [../]
  [./slip_rule]
    type = PowerLawSlipRule
    n = {cp_n}
    gamma0 = {cp_gamma_0}
  [../]
  [./slip_strength]
    type = SingleSlipStrengthMap
    constant_strength = {cp_tau_0}
  [../]
  [./voce_hardening]
    type = VoceSingleSlipHardeningRule
    initial_slope = {cp_slope}
    saturated_hardening = {cp_tau_sat}
  [../]
  [./integrate_slip_hardening]
    type = ScalarBackwardEulerTimeIntegration
    variable = 'state/internal/slip_hardening'
  [../]
  [./integrate_elastic_strain]
    type = SR2BackwardEulerTimeIntegration
    variable = 'state/elastic_strain'
  [../]
  [./integrate_orientation]
    type = WR2ImplicitExponentialTimeIntegration
    variable = 'state/orientation'
  [../]
  [./implicit_rate]
    type = ComposedModel
    models = "euler_rodrigues elasticity orientation_rate resolved_shear
              elastic_stretch plastic_deformation_rate plastic_spin
              sum_slip_rates slip_rule slip_strength voce_hardening
              integrate_slip_hardening integrate_elastic_strain integrate_orientation"
  [../]
  [./implicit_update]
    type = ImplicitUpdate
    implicit_model = 'implicit_rate'
    solver = 'newton'
  [../]
  [./{material_name}]
    type = ComposedModel
    models = 'implicit_update elasticity'
    additional_outputs = 'state/elastic_strain'
  [../]
[]
"""

# VSHAI Class
class Material(__Material__):
    
    def get_material(self, youngs:float, poissons:float) -> str:
        """
        Gets the content for the material file;
        must be overridden
        
        Parameters:
        * `youngs`:   The elastic modulus
        * `poissons`: The poisson ratio
        """
        cp_slope = self.get_param("cp_b") * self.get_param("cp_tau_0") # initial macroscale work hardening slope
        material_content = MATERIAL_FORMAT.format(
            material_name = self.get_name(),
            youngs        = youngs,
            poissons      = poissons,
            lattice_a     = 1.0,
            slip_dir      = "1 1 0",
            slip_plane    = "1 1 1",
            cp_n          = self.get_param("cp_n"),
            cp_gamma_0    = self.get_param("cp_gamma_0"),
            cp_tau_0      = self.get_param("cp_tau_0"),
            cp_tau_sat    = self.get_param("cp_tau_sat"),
            cp_slope      = cp_slope,
        )
        return material_content
    