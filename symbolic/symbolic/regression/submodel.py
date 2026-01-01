"""
 Title:         Submodel
 Description:   Functions for incorporating submodels
 Author:        Janzen Choi

"""

# Libraries
from symbolic.regression.expression import get_expression_info
from pysr import TemplateExpressionSpec

def create_tes(num_inputs:int, submodels:list) -> TemplateExpressionSpec:
    """
    Creates a template expression specification

    Parameters:
    * `num_inputs`: The number of inputs
    * `submodels`:  List of strings representing submodels;
                    Input variables should be named 'x0', 'x1', etc.;
                    Functions should be named 'f0', 'f1', etc.;
                    Can't use [E, Q, S] as parameters

    Returns the template expression specification
    """
    
    # Initialise inputs and functions
    input_list = [f"x{i}" for i in range(num_inputs)]
    function_list = ["f"]

    # Initialise submodel information
    submodel_defs = ""
    num_params_list = []

    # Extract information from each submodel
    for i, submodel in enumerate(submodels):

        # Extract the parameters and functions
        parameters, functions = get_expression_info(submodel)
        function_handles = [str(f.split("(")[0]) for f in functions if f.startswith("f")]
        function_list += function_handles
        num_params_list.append(len(parameters))

        # Define parameters
        if parameters == []:
            parameter_def = ""
        else:
            parameter_def = ", ".join(parameters) + " = " + ", ".join([f"p{i}[{j+1}]" for j in range(len(parameters))])
        
        # Construct combined string
        expression_def = f"y{i} = {submodel}"
        submodel_def = f"{parameter_def}\n{expression_def}\n"
        submodel_defs += submodel_def

    # Define the parameters dict
    parameters_dict = {}
    for i, num_params in enumerate(num_params_list):
        if num_params > 0:
            parameters_dict[f"p{i}"] = num_params

    # Create the combined string 
    combined_str = submodel_defs + "f(" + ", ".join(input_list) + ", "
    combined_str += ", ".join([f"y{j}" for j in range(len(submodels))]) + ")"

    # Define the expression specification and return
    # print(function_list)
    # print(input_list)
    # print(parameters_dict)
    # print(combined_str)
    # exit()
    function_list = list(set(function_list))
    expression_spec = TemplateExpressionSpec(
        expressions    = function_list,
        variable_names = input_list,
        parameters     = parameters_dict,
        combine        = combined_str
    )
    return expression_spec
