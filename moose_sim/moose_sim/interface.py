"""
 Title:         Simulation Interface
 Description:   Interface for running MOOSE simulations
 Author:        Janzen Choi

"""

# Libraries
import inspect, os, re, time
from moose_sim.simulate.controller import Controller

# Interface Class
class Interface:

    def __init__(self, title:str="", input_path:str="./data", output_path:str="./results",
                 verbose:bool=True, output_here:bool=False):
        """
        Class to interact with the optimisation code
        
        Parameters:
        * `title`:       Title of the output folder
        * `input_path`:  Path to the input folder
        * `output_path`: Path to the output folder
        * `verbose`:     If true, outputs messages for each function call
        * `output_here`: If true, just dumps the output in ths executing directory
        """
        
        # Initialise internal variables
        self.__print_index__ = 0
        self.__verbose__     = verbose
        
        # Starting code
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        self.__print__(f"\n  Starting on {time_str}\n", add_index=False)
        self.__start_time__ = time.time()
        time_stamp = time.strftime("%y%m%d%H%M%S", time.localtime(self.__start_time__))
        
        # Define input and output
        self.__input_path__ = input_path
        file_path = inspect.currentframe().f_back.f_code.co_filename
        file_name = file_path.split("/")[-1].replace(".py","")
        title = f"_{file_name}" if title == "" else f"_{title}"
        title = re.sub(r"[^a-zA-Z0-9_]", "", title.replace(" ", "_"))
        self.__output_dir__ = "." if output_here else time_stamp
        self.__output_path__ = "." if output_here else f"{output_path}/{self.__output_dir__}{title}"
        
        # Define input / output functions
        self.__get_input__  = lambda x : f"{self.__input_path__}/{x}"
        self.__get_output__ = lambda x : f"{self.__output_path__}/{x}"
        self.__controller__ = Controller(self.__get_input__, self.__get_output__)
        
        # Create directories
        if not output_here:
            safe_mkdir(output_path)
            safe_mkdir(self.__output_path__)
    
    def define_mesh(self, mesh_file:str, orientation_file:str, degrees:bool=True, active:bool=True) -> None:
        """
        Defining the mesh
        
        Parameters:
        * `mesh_file`:        The name of the mesh file
        * `orientation_file`: The name of the orientation file
        * `degrees`:          Whether the orientation data is in degrees (or radians)
        * `active`:           Whether the orientation data is active (or passive)
        """
        type_str = "deg" if degrees else "rad"
        self.__print__(f"Defining the mesh at '{mesh_file}' with orientations ({type_str}) at '{orientation_file}'")
        self.__controller__.define_mesh(mesh_file, orientation_file, degrees, active)

    def get_dimensions(self) -> dict:
        """
        Gets the dimensions of the defined mesh;
        {"x": x_length, "y": y_length, "z": z_length}
        """
        self.__print__("Getting the dimensions of the defined mesh")
        if self.__controller__.mesh_file == "":
            raise ValueError("The mesh has not been defined!")
        dimensions = self.__controller__.get_dimensions()
        return dimensions

    def define_material(self, material_path:str, material_params:dict={},
                        material_ext:str="xml", **kwargs) -> None:
        """
        Defines the material

        Parameters:
        * `material_path`:   The path to the material
        * `material_params`: Dictionary of parameter values
        * `material_ext`:    Extension to use for the file
        """
        self.__print__(f"Defining the material ({material_path})")
        self.__controller__.define_material(material_path, material_params, material_ext, **kwargs)
    
    def define_simulation(self, simulation_path:str, simulation_params:dict={},
                          simulation_ext:str="i", **kwargs) -> None:
        """
        Defines the simulation

        Parameters:
        * `simulation_path`:   The path to the simulation
        * `simulation_params`: Dictionary of parameter values
        * `simulation_ext`:    Extension to use for the file
        """
        self.__print__(f"Defining the simulation ({simulation_path})")
        self.__controller__.define_simulation(simulation_path, simulation_params, simulation_ext, **kwargs)

    def simulate(self, opt_path:str, num_processors:int, timeout:float=1e10) -> None:
        """
        Runs the simulation

        Parameters:
        * `opt_path`:       Path to the *-opt executable
        * `num_processors`: The number of processors
        * `timeout`:        The maximum amount of time (in seconds) to run the simulation
        """
        self.__print__("Running the simulation")
        self.__check_files__()
        self.__controller__.run_simulation(opt_path, num_processors, self.__output_path__, timeout)

    def export_params(self, params_file:str="params.txt") -> None:
        """
        Exports the parameters

        Parameters:
        * `params_file`: The name of the parameter file
        """
        self.__print__("Exporting the parameters")
        self.__controller__.export_params(params_file)

    def compress_csv(self, sf:int=5, exclude:list=None) -> None:
        """
        Rounds the values in the outputted CSV files

        Parameters:
        * `sf`:      The significant figures to round the values
        * `exclude`: The fields to exclude in the compressed results
        """
        self.__print__(f"Compressing the results")
        self.__check_simulation_run__()
        self.__controller__.compress_csv(sf, exclude)

    def post_process(self, sim_path:str=None, **kwargs) -> None:
        """
        Conducts post processing after the simulation has completed

        Parameters:
        * `sim_path`: The path to conduct the post processing;
                      uses current result path if undefined
        """
        if sim_path == None:
            self.__print__("Conducting post processing on simulation results")
            self.__check_simulation_run__()
        else:
            self.__print__(f"Conducting post processing on '{sim_path}")
        self.__check_files__()
        self.__controller__.post_process(sim_path, **kwargs)

    def remove_files(self, keyword_list:list) -> None:
        """
        Removes files after the simulation ends

        Parameters:
        * `keyword_list`: List of keywords to remove files
        """
        self.__print__("Removing files")
        self.__controller__.remove_files(keyword_list)

    def __check_files__(self) -> None:
        """
        Checks that the mesh, material, and simulation have been defined
        """
        if self.__controller__.mesh_file == "":
            raise ValueError("The mesh has not been defined!")
        if self.__controller__.material_name == "":
            raise ValueError("The material has not been defined!")
        if self.__controller__.simulation_name == "":
            raise ValueError("The simulation has not been defined!")

    def __check_simulation_run__(self) -> None:
        """
        Checks that the simulation has been run
        """
        if not self.__controller__.simulation_run:
            raise ValueError("The simulation has not been run!")

    def __print__(self, message:str, add_index:bool=True) -> None:
        """
        Displays a message before running the command (for internal use only)
        
        Parameters:
        * `message`:   the message to be displayed
        * `add_index`: if true, adds a number at the start of the message
        """
        if not add_index:
            print(message)
        if not self.__verbose__ or not add_index:
            return
        self.__print_index__ += 1
        print(f"   {self.__print_index__})\t{message} ...")
    
    def __del__(self):
        """
        Prints out the final message (for internal use only)
        """
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        duration = round(time.time() - self.__start_time__)
        duration_h = duration // 3600
        duration_m = (duration - duration_h * 3600) // 60
        duration_s = duration - duration_h * 3600 - duration_m * 60
        duration_str_list = [
            f"{duration_h} hours" if duration_h > 0 else "",
            f"{duration_m} mins" if duration_m > 0 else "",
            f"{duration_s} seconds" if duration_s > 0 else ""
        ]
        duration_str = ", ".join([d for d in duration_str_list if d != ""])
        duration_str = f"in {duration_str}" if duration_str != "" else ""
        self.__print__(f"\n  Finished on {time_str} {duration_str}\n", add_index=False)

def safe_mkdir(dir_path:str) -> None:
    """
    For safely making a directory

    Parameters:
    * `dir_path`: The path to the directory
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass
