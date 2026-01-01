"""
 Title:         Simulation
 Description:   For creating simulation files
 Author:        Janzen Choi

"""

# Libraries
import importlib, os, pathlib, sys

# Simulation Class
class __Simulation__:

    def __init__(self, name:str, params:dict, input_function):
        """
        Template class for simulation objects
        
        Parameters:
        * `name`:           The name of the simulation
        * `params`:         The parameter values
        * `input_function`: The input function
        """
        self.name           = name
        self.input_function = input_function
        self.params         = params

    def get_name(self) -> str:
        """
        Gets the name of the simulation
        """
        return self.name
    
    def get_param(self, param_name:str) -> float:
        """
        Gets a parameter value
        """
        if not param_name in self.params.keys():
            raise ValueError(f"The '{param_name}' parameter has not been initialised!")
        return self.params[param_name]
    
    def set_mesh_file(self, mesh_file:str) -> None:
        """
        Sets the name of the mesh file

        Parameters:
        * `mesh_file`: The path to the orientation file
        """
        self.mesh_file = mesh_file

    def get_mesh_file(self) -> str:
        """
        Gets the name of the mesh file
        """
        return self.mesh_file
    
    def set_orientation_file(self, orientation_file:str) -> None:
        """
        Sets the name of the orientation file

        Parameters:
        * `orientation_file`: The path to the orientation file
        """
        self.orientation_file = orientation_file

    def get_orientation_file(self) -> str:
        """
        Gets the name of the orientation file
        """
        return self.orientation_file

    def set_material_file(self, material_file:str) -> None:
        """
        Sets the material file

        Parameters:
        * `material_file`: The material file
        """
        self.material_file = material_file

    def get_material_file(self) -> str:
        """
        Gets the material file
        """
        return self.material_file

    def set_material_name(self, material_name:str) -> None:
        """
        Sets the material name (including/excluding path)

        Parameters:
        * `material_name`: The material name
        """
        self.material_name = material_name

    def get_material_name(self) -> str:
        """
        Gets the material name
        """
        return self.material_name

    def set_csv_file(self, csv_file:str) -> None:
        """
        Sets the name of the CSV file

        Parameters:
        * `csv_file`: The name of the CSV file
        """
        self.csv_file = csv_file

    def get_csv_file(self) -> str:
        """
        Gets the name of the CSV file
        """
        return self.csv_file

    def get_input(self, path:str) -> None:
        """
        Gets the input from a certain file

        Parameters:
        * `path`: The path to the file
        """
        return self.input_function(path)

    def get_simulation(self, **kwargs) -> str:
        """
        Gets the content for the simulation file;
        must be overridden
        """
        raise NotImplementedError

    def post_process(self, sim_path:str, results_path:str, **kwargs) -> None:
        """
        Conducts post processing after the simulation has completed

        Parameters:
        * `sim_path`:     The path to conduct the post processing;
                          uses current result path if undefined
        * `results_path`: The path to current results
        """
        pass

def get_simulation(simulation_path:str, params:dict, get_input_function, mesh_file:str, orientation_file:str,
                   material_file:str, material_name:str, csv_file:str) -> __Simulation__:
    """
    Gets the simulation file's content
    
    Parameters:
    * `simulation_path`:    The path to the simulation
    * `params`:             The parameter values
    * `get_input_function`: The input function
    * `mesh_file`:          The name of the mesh file
    * `orientation_file`:   The name of the orientation file
    * `material_file`:      The name of the material file
    * `material_name`:      The name of the material
    * `csv_file`:           The name of the CSV file
    """

    # Separate simulation file and path
    simulation_file = simulation_path.split("/")[-1]
    simulation_path = "/".join(simulation_path.split("/")[:-1])
    simulations_dir = pathlib.Path(__file__).parent.resolve()
    simulations_dir = f"{simulations_dir}/{simulation_path}"

    # Get available simulations in current folder
    files = os.listdir(simulations_dir)
    files = [file.replace(".py", "") for file in files]
    files = [file for file in files if not file in ["__simulation__", "__pycache__"]]
    
    # Raise error if simulation name not in available simulations
    if not simulation_file in files:
        raise NotImplementedError(f"The simulation '{simulation_file}' has not been implemented")

    # Import and prepare simulation
    module_file = f"{simulations_dir}/{simulation_file}.py"
    spec = importlib.util.spec_from_file_location("simulation_file", module_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Initialise and return the simulation
    from simulation_file import Simulation
    simulation = Simulation(simulation_file, params, get_input_function)
    simulation.set_mesh_file(mesh_file)
    simulation.set_orientation_file(orientation_file)
    simulation.set_material_file(material_file)
    simulation.set_material_name(material_name)
    simulation.set_csv_file(csv_file)
    return simulation
