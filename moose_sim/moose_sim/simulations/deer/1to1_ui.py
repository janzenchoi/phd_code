"""
 Title:         Simulator for a 1:1 mesh with unspecified intervals
 Description:   For creating the CP simulation file
 Author:        Janzen Choi

"""

# Libraries
import numpy as np, re
from moose_sim.analyse.summarise import get_csv_results, get_block_ids, map_field
from moose_sim.analyse.summarise import get_average_euler, map_average_field, map_total_field
from moose_sim.helper.general import transpose
from moose_sim.helper.io import csv_to_dict, dict_to_csv
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
  [./mesh_input]
    type         = FileMeshGenerator
    file         = '{mesh_file}'
  [../]
  [./add_side_sets]
    input        = mesh_input
    type         = SideSetsFromNormalsGenerator
    fixed_normal = true
    new_boundary = 'x0 x1'
    normals      = '-1 0 0 1 0 0'
  [../]
  [./add_subdomain_ids]
    type         = SubdomainExtraElementIDGenerator
    input        = add_side_sets
    subdomains   = '{block_ids}'
    extra_element_id_names = 'block_id'
    extra_element_ids = '{block_ids}'
  [../]
  [./add_z_hold_side_set]
    input        = add_subdomain_ids
    type         = SideSetsAroundSubdomainGenerator
    new_boundary = 'z0'
    fixed_normal = true
    normal       = '0 0 -1'
    block        = '{grip_ids}'
  [../]
  [./add_y_hold_side_set]
    input        = add_z_hold_side_set
    type         = SideSetsAroundSubdomainGenerator
    new_boundary = 'y0'
    fixed_normal = true
    normal       = '0 -1 0'
    block        = '{grip_ids}'
  [../]
[]

# ==================================================
# Define Initial Orientations
# ==================================================

# Element orientations
[UserObjects]
  [./euler_angle_file]
    type           = ElementPropertyReadFile
    nprop          = 3
    prop_file_name = '{orientation_file}'
    read_type      = element
    use_zero_based_block_indexing = false
  [../]
[]

# ==================================================
# Define Modules
# ==================================================

[Modules]
  [./TensorMechanics]
    [./Master]
      [./all]
        strain          = FINITE
        formulation     = TOTAL
        add_variables   = true
        new_system      = true
        volumetric_locking_correction = true # linear hex elements
        generate_output = 'elastic_strain_xx strain_xx cauchy_stress_xx mechanical_strain_xx'
      [../]
    [../]
  [../]
[]

# ==================================================
# Define Variables
# ==================================================

[AuxVariables]
  [./block_id]
    family = MONOMIAL
    order  = CONSTANT
  [../]
  [./volume]
    order  = CONSTANT
    family = MONOMIAL
  [../]
  [./orientation_q1]
    order  = CONSTANT
    family = MONOMIAL
  [../]
  [./orientation_q2]
    order  = CONSTANT
    family = MONOMIAL
  [../]
  [./orientation_q3]
    order  = CONSTANT
    family = MONOMIAL
  [../]
  [./orientation_q4]
    order  = CONSTANT
    family = MONOMIAL
  [../]
[]

# ==================================================
# Define Kernels
# ==================================================

[AuxKernels]
  [block_id]
    type          = ExtraElementIDAux
    variable      = block_id
    extra_id_name = block_id
  [../]
  [volume]
    type = VolumeAux
    variable = volume
  []
  [q1]
    type       = MaterialStdVectorAux
    property   = orientation
    index      = 0
    variable   = orientation_q1
    execute_on = 'initial timestep_end'
    block      = '{grain_ids}'
  [../]
  [q2]
    type       = MaterialStdVectorAux
    property   = orientation
    index      = 1
    variable   = orientation_q2
    execute_on = 'initial timestep_end'
    block      = '{grain_ids}'
  [../]
  [q3]
    type       = MaterialStdVectorAux
    property   = orientation
    index      = 2
    variable   = orientation_q3
    execute_on = 'initial timestep_end'
    block      = '{grain_ids}'
  [../]
  [q4]
    type       = MaterialStdVectorAux
    property   = orientation
    index      = 3
    variable   = orientation_q4
    execute_on = 'initial timestep_end'
    block      = '{grain_ids}'
  [../]
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
# Define Material
# ==================================================

[Materials]
  [./stress1]
    type               = NEMLCrystalPlasticity
    database           = '{material_file}'
    model              = '{material_name}_cp'
    large_kinematics   = true
    euler_angle_reader = euler_angle_file
    angle_convention   = 'bunge'
    block              = '{grain_ids}'
  [../]
  [./stress2]
    type             = CauchyStressFromNEML
    database         = '{material_file}'
    model            = '{material_name}_vp'
    large_kinematics = true
    block            = '{grip_ids}'
  [../]
[]

# ==================================================
# Define Preconditioning
# ==================================================

[Preconditioning]
  [./SMP]
    type = SMP
    full = true
  [../]
[]

# ==================================================
# Define Postprocessing (History)
# ==================================================

[VectorPostprocessors]
  [./element]
    type     = ElementValueSampler
    variable = 'block_id volume
                orientation_q1 orientation_q2 orientation_q3 orientation_q4
                cauchy_stress_xx strain_xx elastic_strain_xx mechanical_strain_xx'
    contains_complete_history = false
    execute_on = 'INITIAL TIMESTEP_END'
    sort_by    = id
    block      = '{block_ids}'
  [../]
[]

# ==================================================
# Define Postprocessing (Average Response)
# ==================================================

[Postprocessors]

  # Total Strain
  [./mTE_cpvp_xx]
    type     = ElementAverageValue
    variable = strain_xx
  [../]
  [./mTE_cp_xx]
    type     = ElementAverageValue
    variable = strain_xx
    block    = '{grain_ids}'
  [../]
  [./mTE_vp_xx]
    type     = ElementAverageValue
    variable = strain_xx
    block    = '{grip_ids}'
  [../]

  # Cuachy Stress
  [./mCS_cpvp_xx]
    type     = ElementAverageValue
    variable = cauchy_stress_xx
  [../]
  [./mCS_cp_xx]
    type     = ElementAverageValue
    variable = cauchy_stress_xx
    block    = '{grain_ids}'
  [../]
  [./mCS_vp_xx]
    type     = ElementAverageValue
    variable = cauchy_stress_xx
    block    = '{grip_ids}'
  [../]

  # Elastic Strain
  [./mEE_cpvp_xx]
    type     = ElementAverageValue
    variable = elastic_strain_xx
  [../]
  [./mEE_cp_xx]
    type     = ElementAverageValue
    variable = elastic_strain_xx
    block    = '{grain_ids}'
  [../]
  [./mEE_vp_xx]
    type     = ElementAverageValue
    variable = elastic_strain_xx
    block    = '{grip_ids}'
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
  # exodus = true
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
        * `end_strain`: The final (engineering) strain
        """

        # Get orientation data
        orientation_file = self.get_orientation_file()
        orientation_info = np.loadtxt(self.get_input(orientation_file), delimiter=",")
        orientation_info = transpose(orientation_info)

        # Get IDs
        block_ids = list(set([int(block_id) for block_id in orientation_info[4]]))
        grain_ids = block_ids[:-2]
        grip_ids  = block_ids[-2:]
        
        # Define simulation file
        simulation_content = SIMULATION_FORMAT.format(

            # File names
            mesh_file        = self.get_mesh_file(),
            orientation_file = orientation_file,
            material_file    = self.get_material_file(),
            material_name    = self.get_material_name(),
            csv_file         = self.get_csv_file(),
            
            # Block IDs
            block_ids  = " ".join([str(id) for id in block_ids]),
            grain_ids  = " ".join([str(id) for id in grain_ids]),
            grip_ids   = " ".join([str(id) for id in grip_ids]),

            # Temporal parameters
            start_time = 0,
            end_time   = end_time,
            dt_start   = 1e0,
            dt_min     = 1e-2,
            dt_max     = end_time,

            # Other parameters
            end_strain = end_strain,
        )
        return simulation_content

    def post_process(self, sim_path:str, results_path:str, grain_map_path:str=None) -> None:
        """
        Conducts post processing after the simulation has completed

        Parameters:
        * `sim_path`:       The path to conduct the post processing;
                            uses current result path if undefined
        * `results_path`:   The path to current results
        * `grain_map_path`: The path to the grain map so that the grain IDs are consistent
        """

        # Initialise summary
        results_dict  = csv_to_dict(f"{sim_path}/results.csv")
        sim_dict_list = get_csv_results(sim_path, "results_element", "time")
        block_ids = get_block_ids(sim_dict_list[-1], "block_id")
        grain_field_map = map_field(sim_dict_list[-1], "block_id", "id", block_ids[:-2])

        # Calculate average stresses and elastic strains
        average_dict = {
            "average_strain":        results_dict["mTE_cpvp_xx"],
            "average_grain_strain":  results_dict["mTE_cp_xx"],
            "average_grip_strain":   results_dict["mTE_vp_xx"],
            "average_stress":        results_dict["mCS_cpvp_xx"],
            "average_grain_stress":  results_dict["mCS_cp_xx"],
            "average_grip_stress":   results_dict["mCS_vp_xx"],
            "average_elastic":       results_dict["mEE_cpvp_xx"],
            "average_grain_elastic": results_dict["mEE_cp_xx"],
            "average_grip_elastic":  results_dict["mEE_vp_xx"]
        }

        # Calculate stress and elastic strain in each grain
        as_dict = map_average_field(sim_dict_list, "cauchy_stress_xx", grain_field_map, "volume")
        as_dict = {f"g{k}_stress": v for k, v in as_dict.items()}
        es_dict = map_average_field(sim_dict_list, "elastic_strain_xx", grain_field_map, "volume")
        es_dict = {f"g{k}_elastic": v for k, v in es_dict.items()}

        # Calculate total volume of each grain
        volume_dict = map_total_field(sim_dict_list, "volume", grain_field_map)
        volume_dict = {f"g{k}_volume": v for k, v in volume_dict.items()}
        
        # Calculate average orientations in each grain
        orientation_fields = [f"orientation_q{i}" for i in [1,2,3,4]]
        average_euler_dict = get_average_euler(sim_dict_list, orientation_fields, grain_field_map, "volume", False)
        phi_dict = {}
        for grain_id in average_euler_dict.keys():
            euler_list = average_euler_dict[grain_id]
            for i, phi in enumerate(["phi_1", "Phi", "phi_2"]):
                field = f"g{grain_id}_{phi}"
                phi_dict[field] = [euler[i] for euler in euler_list]

        # Combine all summaries and convert grain IDs if defined
        summary_dict = {**average_dict, **as_dict, **es_dict, **volume_dict, **phi_dict}
        if grain_map_path != None:
            
            # Initialise conversion
            grain_map = csv_to_dict(grain_map_path)
            new_summary_dict = {}
            mesh_to_ebsd = dict(zip(grain_map["mesh_id"], grain_map["ebsd_id"]))
            
            # Iterate through keys
            for key in summary_dict:
                if bool(re.match(r'^g\d+.*$', key)):
                    key_list = key.split("_")
                    mesh_id = int(key_list[0].replace("g",""))
                    new_key = f"g{int(mesh_to_ebsd[mesh_id])}_{'_'.join(key_list[1:])}"
                    new_summary_dict[new_key] = summary_dict[key]
                else:
                  new_summary_dict[key] = summary_dict[key]
              
            # Replace old summary
            summary_dict = new_summary_dict
        
        # Save the summaries
        dict_to_csv(summary_dict, f"{results_path}/summary.csv")
