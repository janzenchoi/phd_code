"""
 Title:         NEML2 simulation for a 1:1 mesh
 Description:   For creating the simulation file
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from moose_sim.helper.general import transpose
from moose_sim.simulations.__simulation__ import __Simulation__

# Format for defining simulations
SIMULATION_FORMAT = """
# ==================================================
# Define global parameters
# ==================================================

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

# ==================================================
# Define Mesh
# ==================================================

[Mesh]
  use_displaced_mesh = false
  [./mesh_file]
    type         = FileMeshGenerator
    file         = '{mesh_file}'
  [../]
  [./x_side_sets]
    input        = mesh_file
    type         = SideSetsFromNormalsGenerator
    fixed_normal = true
    new_boundary = 'x0 x1'
    normals      = '-1 0 0 1 0 0'
  [../]
  [./y_side_sets]
    input        = x_side_sets
    type         = SideSetsFromNormalsGenerator
    fixed_normal = true
    new_boundary = 'y0'
    normals      = '0 -1 0'
  [../]
  [./z_side_sets]
    input        = y_side_sets
    type         = SideSetsFromNormalsGenerator
    fixed_normal = true
    new_boundary = 'z0'
    normals      = '0 0 -1'
  [../]
[]

# ==================================================
# Define Initial Orientations
# ==================================================

# ==================================================
# Define Materials
# ==================================================

[NEML2]
  input = '{material_file}'
  model = '{material_name}'
  verbose = true
  mode = PARSE_ONLY
  device = 'cpu'
[]

[UserObjects]
  active = 'model input_strain'
  [input_strain]
    type = MOOSERankTwoTensorMaterialPropertyToNEML2
    moose_material_property = mechanical_strain
    neml2_variable = forces/E
  []
  [model]
    type = ExecuteNEML2Model
    model = '{material_name}'
    gather_uos = 'input_strain'
  []
[]

[Materials]
  active = 'output_stress_jacobian'
  [output_stress_jacobian]
    type = NEML2StressToMOOSE
    execute_neml2_model_uo = model
    neml2_stress_output = state/S
    neml2_strain_input = forces/E
  []
[]

# ==================================================
# Define Physics
# ==================================================

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

# ==================================================
# Apply stress
# ==================================================

[Functions]
  [./applied_load]
    type = PiecewiseLinear
    x    = '0 {end_time}'
    y    = '0 {end_strain}'
  [../]
[]

# ==================================================
# Boundary Conditions
# ==================================================

[BCs]
  [./z0hold]
    type     = DirichletBC
    boundary = 'z0'
    variable = disp_z
    value    = 0.0
  [../]
  [./y0hold]
    type     = DirichletBC
    boundary = 'y0'
    variable = disp_y
    value    = 0.0
  [../]
  [./x0hold]
    type     = DirichletBC
    boundary = 'x0'
    variable = disp_x
    value    = 0.0
  [../]
  [./x1load]
    type     = FunctionDirichletBC
    boundary = 'x1'
    variable = disp_x
    function = applied_load
    preset   = false
  [../]
[]

# ==================================================
# Dampers
# ==================================================

[Dampers]
  [./damper]
    type = ReferenceElementJacobianDamper
    max_increment = 0.005 # 0.002
    displacements = 'disp_x disp_y disp_z'
  [../]
[]

# ==================================================
# Define Executioner
# ==================================================

[Executioner]
  
  # Transient (time-dependent) and multi-physics problem
  type = Transient
  automatic_scaling = true # false
  compute_scaling_once = true

  # Solver
  solve_type = NEWTON # NEWTON (Newton-Raphson), PJFNK, FD
  residual_and_jacobian_together = true
  
  # Options for PETSc (to solve linear equations)
  # petsc_options       = '-snes_converged_reason -ksp_converged_reason' 
  # petsc_options_iname = '-pc_type -pc_factor_mat_solver_package -ksp_type'
  # petsc_options_value = 'lu superlu_dist gmres' # lu better for few elements
  # reuse_preconditioner = true
  # reuse_preconditioner_max_linear_its = 20
  petsc_options       = '-snes_converged_reason -ksp_converged_reason' 
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package -ksp_gmres_restart 
                         -pc_hypre_boomeramg_strong_threshold -pc_hypre_boomeramg_interp_type -pc_hypre_boomeramg_coarsen_type 
                         -pc_hypre_boomeramg_agg_nl -pc_hypre_boomeramg_agg_num_paths -pc_hypre_boomeramg_truncfactor'
  petsc_options_value = 'hypre boomeramg 200 0.7 ext+i PMIS 4 2 0.4'

  # Solver tolerances
  l_max_its     = 500 
  l_tol         = 1e-4 # 1e-6
  nl_max_its    = 16
  nl_rel_tol    = 1e-5 # 1e-6
  nl_abs_tol    = 1e-5 # 1e-6
  nl_forced_its = 1
  # n_max_nonlinear_pingpong = 1
  line_search   = 'none' # 'bt'

  # Time variables
  start_time = {start_time}
  end_time   = {end_time}
  dtmin      = {dt_min}
  dtmax      = {dt_max}

  # Simulation speed up
  [./Predictor]
    type  = SimplePredictor
    scale = 1.0
    skip_after_failed_timestep = true # false
  [../]

  # Timestep growth
  [./TimeStepper]
    type                   = IterationAdaptiveDT
    growth_factor          = 1.5
    cutback_factor         = 0.67
    linear_iteration_ratio = 100000000000
    optimal_iterations     = 8
    iteration_window       = 1
    dt                     = {dt_start}
  [../]
[]

# ==================================================
# Define Simulation Output
# ==================================================

[Outputs]
  exodus = true
  print_linear_residuals = false
  [./console]
    type        = Console
    output_linear = false
    print_mesh_changed_info = false
  [../]
  [./outfile]
    type        = CSV
    file_base   = '{csv_file}'
    time_data   = true
    delimiter   = ','
    execute_on  = 'timestep_end'
  [../]
[]
"""

# CP Model Class
class Simulation(__Simulation__):
    
    def get_simulation(self, end_time:float, end_strain:float) -> str:
        """
        Gets the content for the simulation file;
        must be overridden

        Parameters:
        * `end_time`:   The final time
        * `end_strain`: The final strain
        """
        
        
        # Get orientation data
        orientation_file = self.get_orientation_file()
        orientation_info = np.loadtxt(self.get_input(orientation_file), delimiter=",")
        orientation_info = transpose(orientation_info)

        # # Get IDs
        # block_ids = list(set([int(block_id) for block_id in orientation_info[4]]))
        # grain_ids = block_ids[:-2]
        # grip_ids  = block_ids[-2:]
        
        # Define simulation file
        simulation_content = SIMULATION_FORMAT.format(
            
            # File names
            mesh_file     = self.get_mesh_file(),
            material_name = self.get_material_name(),
            material_file = self.get_material_file(),
            csv_file      = self.get_csv_file(),
            
            # Temporal parameters
            start_time = 0,
            end_time   = end_time,
            dt_start   = 1e0,
            dt_min     = 1e-2,
            dt_max     = end_time,

            # Other parameters
            end_strain = end_strain,
        )
        
        # Return simulation data
        return simulation_content