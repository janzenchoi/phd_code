"""
 Title:         The PyTorch Surrogate for the VoceSlipHardening + AsaroInelasticity + Damage Model
 Description:   Incorporates elasto-viscoplasticity
 Author:        Janzen Choi

"""

# Libraries
import torch, numpy as np, math
from opt_all.models.__model__ import __Model__
from opt_all.helper.general import quick_spline, csv_to_dict

# Constants
NUM_PARAMS = 5

# The Elastic Visco Plastic Class
class Model(__Model__):

    def initialise(self, sm_paths:list, map_paths:list) -> None:
        """
        Constructor for the surrogate model

        Parameters:
        * `sm_paths`:  The list of paths to the surrogate model
        * `map_paths`: The list of paths to the mapping methods
        """
        import sys; sys.path += ["/mnt/c/Users/Janzen/Desktop/code/mms/"]
        self.tc_model, self.tc_input_map, self.tc_output_map = get_sm_info(sm_paths[0], map_paths[0], NUM_PARAMS)
        self.phi_model, self.phi_input_map, self.phi_output_map = get_sm_info(sm_paths[1], map_paths[1], NUM_PARAMS)
        self.grain_ids = [int(output.replace("g","").replace("_1p0_phi_1",""))
                          for output in self.phi_output_map["param_name"] if "_1p0_phi_1" in output]

    def get_response(self, tau_sat:float, b:float, tau_0:float, gamma_0:float, n:float) -> dict:
        """
        Gets the response of the model from the parameters

        Parameters:
        * `tau_sat`: VoceSlipHardening parameter
        * `b`:       VoceSlipHardening parameter
        * `tau_0`:   VoceSlipHardening parameter
        * `gamma_0`: AsaroInelasticity parameter
        * `n`:       AsaroInelasticity parameter
        
        Returns the response as a dictionary
        """

        # Get outputs for tensile model
        param_list = [tau_sat, b, tau_0, gamma_0, n]
        tc_output = get_output(param_list, self.tc_input_map, self.tc_output_map, self.tc_model)
        if tc_output == None:
            return
        
        # Process tensile model outputs
        strain_end, stress_list = tc_output[0], tc_output[1:]
        strain_list = list(np.linspace(0, strain_end, len(stress_list)))
        strain_intervals = [strain*strain_end for strain in [0.2, 0.4, 0.6, 0.8, 1.0]]
        stress_intervals = [quick_spline(strain_list, stress_list, strain) for strain in strain_intervals]
        tc_response = {"strain": [0] + strain_intervals, "stress": [0] + stress_intervals}

        # Get outputs for orientation model
        phi_output = get_output(param_list, self.phi_input_map, self.phi_output_map, self.phi_model)
        phi_response = {}
        for i, grain_id in enumerate(self.grain_ids):
            for j in range(3):
                field = f"g{grain_id}_{['phi_1', 'Phi', 'phi_2'][j]}"
                start = self.get_data(field)[0]
                phi_list = [start] + phi_output[i*15+j*5:i*15+(j+1)*5]
                phi_response[field] = phi_list

        # Combine responses and return
        combined_response = {**tc_response, **phi_response}
        return combined_response

def get_output(input_list:list, input_map:dict, output_map:dict, model) -> list:
    """
    Gets the outputs of the surrogate model

    Parameters:
    * `input_list`: The list of raw input values
    * `input_map`:  The map for the input values
    * `output_map`: The map for the output values
    * `model`:      The surrogate model

    Returns the outputs
    """

    # Process inputs
    processed_input_list = []
    for i in range(len(input_list)):
        try:
            input_value = math.log(input_list[i]) / math.log(input_map["base"][i])
            input_value = linear(input_value, input_map, linear_map, i)
        except ValueError:
            return None
        processed_input_list.append(input_value)
    
    # Get raw outputs and process
    input_tensor = torch.tensor(processed_input_list)
    with torch.no_grad():
        output_list = model(input_tensor).tolist()
    for i in range(len(output_list)):
        try:
            output_list[i] = linear(output_list[i], output_map, linear_unmap, i)
            output_list[i] = math.pow(output_map["base"][i], output_list[i])
        except ValueError:
            return None
    
    # Return the list of outputs
    return output_list

def linear(value:float, map:dict, mapper, index:int) -> float:
    """
    Linearly maps or unmaps a value

    Parameters:
    * `value`:  The value to be mapped / unmapped
    * `map`:    The mapping information
    * `mapper`: The mapping function handler
    * `index`:  The index of the map
    """
    return mapper(
        value = value,
        in_l  = map["in_l_bound"][index],
        in_u  = map["in_u_bound"][index],
        out_l = map["out_l_bound"][index],
        out_u = map["out_u_bound"][index],
    )

def get_sm_info(sm_path:str, map_path:str, num_inputs:int) -> tuple:
    """
    Loads the model and maps given two paths

    Parameters:
    * `sm_path`:    Path to the surrogate model
    * `map_path`:   Path to the map
    * `num_inputs`: Number of inputs

    Returns the surrogate model, the input map, and the output map
    """

    # Load surrogate model
    model = torch.load(sm_path)
    model.eval()
    
    # Load maps
    map_dict = csv_to_dict(map_path)
    input_map_dict, output_map_dict = {}, {}
    for key in map_dict.keys():
        input_map_dict[key] = map_dict[key][:num_inputs]
        output_map_dict[key] = map_dict[key][num_inputs:]

    # Return everything
    return model, input_map_dict, output_map_dict

def linear_map(value:float, in_l:float, in_u:float, out_l:float, out_u:float) -> float:
    """
    Linearly maps a value

    Parameters:
    * `value`:  The value to be mapped
    * `in_l`:   The lower bound of the input
    * `in_u`:   The upper bound of the input
    * `out_l`:  The lower bound of the output
    * `out_u`:  The upper bound of the output

    Returns the mapped value
    """
    if in_l == in_u or out_l == out_u:
        return value
    factor = (out_u - out_l) / (in_u - in_l)
    return (value - in_l) * factor + out_l

def linear_unmap(value:float, in_l:float, in_u:float, out_l:float, out_u:float) -> float:
    """
    Linearly unmaps a value

    Parameters:
    * `value`:  The value to be unmapped
    * `in_l`:   The lower bound of the input
    * `in_u`:   The upper bound of the input
    * `out_l`:  The lower bound of the output
    * `out_u`:  The upper bound of the output

    Returns the unmapped value
    """
    if in_l == in_u or out_l == out_u:
        return value
    factor = (out_u - out_l) / (in_u - in_l)
    return (value - out_l) / factor + in_l

# Custom PyTorch model
class CustomModel(torch.nn.Module):
    
    def __init__(self, input_size:int, output_size:int, hidden_sizes:list):
        """
        Defines the structure of the neural network
        
        Parameters:
        * `input_size`: The number of inputs
        * `output_size`: The number of outputs
        * `hidden_sizes`: List of number of nodes for the hidden layers
        """
        super(CustomModel, self).__init__()
        self.input_layer   = torch.nn.Linear(input_size, hidden_sizes[0])
        self.hidden_layers = [torch.nn.Linear(hidden_sizes[i], hidden_sizes[i+1])
                              for i in range(len(hidden_sizes)-1)]
        self.output_layer  = torch.nn.Linear(hidden_sizes[-1], output_size)
    
    def forward(self, input_tensor:torch.Tensor) -> torch.Tensor:
        """
        Runs the forward pass
        
        Parameters:
        * `input_tensor`: PyTorch tensor for neural network input
        
        Returns the output of the network as a tensor
        """
        output_tensor = torch.relu(self.input_layer(input_tensor))
        for layer in self.hidden_layers:
            output_tensor = torch.relu(layer(output_tensor))
        output_tensor = self.output_layer(output_tensor)
        return output_tensor
