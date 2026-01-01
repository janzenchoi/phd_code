"""
 Title:         Test Simulation for NEML2
 Description:   For creating the simulation file;
                Based on moose/modules/solid_mechanics/test/tests/neml2/fem.i
 Author:        Janzen Choi

"""

# Libraries
from moose_sim.simulations.__simulation__ import __Simulation__

# Format for defining simulations
SIMULATION_FORMAT = """
[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [gmg]
    type = GeneratedMeshGenerator
    dim = 3
    nx = {N}
    ny = {N}
    nz = {N}
  []
[]

[NEML2]
  input = '{material_file}'
  model = '{material_name}'
  temperature = 'T'
  verbose = true
  mode = ELEMENT
  device = 'cpu'
[]

[AuxVariables]
  [T]
  []
[]

[Physics]
  [SolidMechanics]
    [QuasiStatic]
      [all]
        strain = SMALL
        new_system = true
        add_variables = true
        formulation = TOTAL
        volumetric_locking_correction = true
      []
    []
  []
[]

[BCs]
  [xfix]
    type = DirichletBC
    variable = disp_x
    boundary = left
    value = 0
  []
  [yfix]
    type = DirichletBC
    variable = disp_y
    boundary = bottom
    value = 0
  []
  [zfix]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []
  [xdisp]
    type = FunctionDirichletBC
    variable = disp_x
    boundary = right
    function = t
    preset = false
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  automatic_scaling = true
  dt = 1e-3
  dtmin = 1e-3
  num_steps = 5
  residual_and_jacobian_together = true
[]

[Outputs]
  file_base = 'viscoplasticity_isoharden'
  exodus = true
[]
"""

# CP Model Class
class Simulation(__Simulation__):
    
    def get_simulation(self) -> str:
        """
        Gets the content for the simulation file;
        must be overridden
        """
        simulation_content = SIMULATION_FORMAT.format(
            N             = 2,
            material_file = self.get_material_file(),
            material_name = self.get_material_name(),
        )
        return simulation_content