"""
 Title:         Controller
 Description:   Controller for the Deer Simulator
 Author:        Janzen Choi

"""

# Libraries
import os, subprocess, shutil, numpy as np
from moose_sim.helper.io import csv_to_dict, dict_to_csv
from moose_sim.helper.general import transpose, round_sf
from moose_sim.maths.exodus import get_exodus_length
from moose_sim.maths.orientation import rad_to_deg, deg_to_rad
from moose_sim.maths.neml import reorient_euler
from moose_sim.materials.__material__ import get_material
from moose_sim.simulations.__simulation__ import get_simulation

# The Controller class
class Controller():

    def __init__(self, get_input, get_output):
        """
        Class to control all the components of the simulation

        Parameters:
        * `get_input`:  Function to get the path to the input files
        * `get_output`: Function to get the path to the output files
        """

        # Initialise internal variables
        self.get_input         = get_input
        self.get_output        = get_output
        self.mesh_file         = ""
        self.orientation_file  = ""
        self.material_file     = "material"
        self.material_name     = ""
        self.material_params   = {}
        self.simulation_file   = "simulation"
        self.simulation_name   = ""
        self.simulation_params = {}
        self.simulation        = None
        self.simulation_run    = False
        self.material_ext      = ""
        self.simulation_ext    = ""
        
        # Initialise file paths
        self.material_path   = ""
        self.simulation_path = ""
        self.csv_file        = "results"
        self.analysis_file   = "analysis_plot"
        self.csv_path        = get_output(f"{self.csv_file}.csv")
        self.analysis_path   = get_output(self.analysis_file)

    def define_mesh(self, mesh_file:str, orientation_file:str, degrees:bool=True, active:bool=True) -> None:
        """
        Defining the mesh
        
        Parameters:
        * `mesh_file`:        The name of the mesh file
        * `orientation_file`: The name of the orientation file
        * `degrees`:          Whether the orientation data is in degrees
        * `active`:           Whether the orientation data is active (or passive)
        """

        # Get paths to input files
        self.mesh_file = mesh_file
        self.orientation_file = orientation_file
        mesh_path = self.get_input(mesh_file)
        orientation_path = self.get_input(orientation_file)
        
        # Check if files exist
        if not os.path.exists(mesh_path):
            raise FileNotFoundError(f"No mesh file exists at '{mesh_path}'!")
        if not os.path.exists(orientation_path):
            raise FileNotFoundError(f"No orientation file exists at '{mesh_path}'!")
        
        # Read orientation file
        ori_list = np.loadtxt(orientation_path, delimiter=",")
        euler_list = [list(ori[:3]) for ori in ori_list]
        
        # Enforce degrees and active rotations, then round
        if not degrees and not active:
            euler_list = [reorient_euler(euler) for euler in euler_list]
            euler_list = rad_to_deg(euler_list)
        elif degrees and not active:
            euler_list = deg_to_rad(euler_list)
            euler_list = [reorient_euler(euler) for euler in euler_list]
            euler_list = rad_to_deg(euler_list)
        elif not degrees and active:
            euler_list = rad_to_deg(euler_list)
        euler_list = [[round_sf(e, 5) for e in euler] for euler in euler_list]
        
        # Store and save orientation information to results folder
        euler_list = transpose(euler_list)
        ori_dict = {"phi_1": euler_list[0], "Phi": euler_list[1], "phi_2": euler_list[2]}
        other_list = transpose([list(ori[3:]) for ori in ori_list])
        other_dict = dict(zip([str(i) for i in range(len(other_list))], other_list))
        dict_to_csv({**ori_dict, **other_dict}, self.get_output(orientation_file), add_header=False)

        # Copy the mesh to the results folder
        shutil.copy(mesh_path, self.get_output(mesh_file))

    def get_dimensions(self) -> dict:
        """
        Gets the dimensions of the defined mesh;
        {"x": x_length, "y": y_length, "z": z_length}
        """
        mesh_path = self.get_input(self.mesh_file)
        dimensions = {
            "x": get_exodus_length(mesh_path, "x"),
            "y": get_exodus_length(mesh_path, "y"),
            "z": get_exodus_length(mesh_path, "z"),
        }
        return dimensions

    def define_material(self, material_path:str, material_params:dict,
                        material_ext:str, **kwargs) -> None:
        """
        Defines the material

        Parameters:
        * `material_path`:   The path to the material
        * `material_params`: Dictionary of parameter values
        * `material_ext`:    Extension to use for the file
        """

        # Save material information
        self.material_name   = material_path.split("/")[-1]
        self.material_params = material_params
        self.material_ext    = material_ext
        self.material_path   = self.get_output(f"{self.material_file}.{self.material_ext}")

        # Write the material file
        material_content = get_material(material_path, material_params, **kwargs)
        with open(self.material_path, "w+") as fh:
            fh.write(material_content)

    def define_simulation(self, simulation_path:str, simulation_params:dict,
                          simulation_ext:str, **kwargs) -> None:
        """
        Defines the simulation

        Parameters:
        * `simulation_path`:   The path to the simulation
        * `simulation_params`: Dictionary of parameter values
        * `simulation_ext`:    Extension to use for the file
        """

        # Save simulation information
        self.simulation_name   = simulation_path.split("/")[-1]
        self.simulation_params = simulation_params
        self.simulation_ext    = simulation_ext
        self.simulation_path   = self.get_output(f"{self.simulation_file}.{self.simulation_ext}")

        # Write the simulation file
        self.simulation = get_simulation(simulation_path, simulation_params, self.get_input,
                                         self.mesh_file, self.orientation_file, f"{self.material_file}.{self.material_ext}", 
                                         self.material_name, self.csv_file)
        simulation_content = self.simulation.get_simulation(**kwargs)
        with open(self.simulation_path, "w+") as fh:
            fh.write(simulation_content)

    def run_simulation(self, opt_path:str, num_processors:int, output_path:str, timeout:float) -> None:
        """
        Runs the simulation

        Parameters:
        * `opt_path`:       Path to the *-opt executable
        * `num_processors`: The number of processors
        * `output_path`:    Path to the output directory
        * `timeout`:        The maximum amount of time (in seconds) to run the simulation
        """

        # Check that the material and simulation are both defined
        if self.material_name == "":
            raise NotImplementedError("The material name has not been defined!")
        if self.simulation_name == "":
            raise NotImplementedError("The simulation name has not been defined!")

        # Run the simulation
        current_dir = os.getcwd()
        os.chdir("{}/{}".format(os.getcwd(), output_path))
        command = f"timeout {timeout}s mpiexec -np {num_processors} {opt_path} -i {self.simulation_file}.{self.simulation_ext}"
        print(f"\n  Running '{command}'\n")
        subprocess.run([command], shell=True, check=False)
        # try:
        #     subprocess.run([command], shell=True, check=False)
        # except:
        #     pass
        os.chdir(current_dir)
        self.simulation_run = True

    def compress_csv(self, sf:int=5, exclude:list=None) -> None:
        """
        Rounds the values in the outputted CSV files

        Parameters:
        * `sf`:      The significant figures to round the values
        * `exclude`: The fields to exclude in the compressed results
        """
        results_dir = self.get_output("")
        csv_paths = [f"{results_dir}/{csv_file}" for csv_file in os.listdir(results_dir) if csv_file.endswith(".csv")]
        for csv_path in csv_paths:
            data_dict = csv_to_dict(csv_path)
            new_dict = {}
            for key in data_dict.keys():
                if exclude == None or not key in exclude:
                    new_dict[key] = round_sf(data_dict[key], sf)
            dict_to_csv(new_dict, csv_path)

    def post_process(self, sim_path:str, **kwargs) -> None:
        """
        Conducts post processing after the simulation has completed

        Parameters:
        * `sim_path`: The path to conduct the post processing;
                      uses current result path if undefined
        """
        sim_path = self.get_output("") if sim_path == None else sim_path
        try:
            self.simulation.post_process(sim_path, self.get_output(""), **kwargs)
        except:
            pass

    def remove_files(self, keyword_list:list) -> None:
        """
        Removes files after the simulation ends

        Parameters:
        * `keyword_list`: List of keywords to remove files
        """
        file_list = os.listdir(self.get_output(""))
        for keyword in keyword_list:
            for file_name in file_list:
                if keyword in file_name:
                    file_path = self.get_output(file_name)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except:
                        pass

    def export_params(self, params_file:str) -> None:
        """
        Exports the parameters

        Parameters:
        * `params_file`: The name of the parameter file
        """
        
        # Prepare path and content
        params_path = self.get_output(params_file)
        params_dict = {**self.material_params, **self.simulation_params}

        # Write parameters to file
        with open(params_path, "w+") as fh:
            for param_name in params_dict.keys():
                fh.write(f"{param_name}: {params_dict[param_name]}\n")
