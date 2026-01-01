"""
 Title:         Expression
 Description:   Contains expression related functions
 Author:        Janzen Choi

"""

# Libraries
from symbolic.helper.general import round_sf
from symbolic.helper.plotter import save_plot
from copy import deepcopy
import matplotlib.pyplot as plt, re
from sympy import sympify, latex
from sympy.parsing.sympy_parser import parse_expr

def replace_variables(latex_string:str, variable_map:dict) -> str:
    """
    Replaces variable names inside a latex string

    Parameters:
    * `latex_string`: The latex string; can also be a list/dictionary of strings
    * `variable_map`: Dictionary mapping variable names to new names

    Returns the replaced latex string
    """
    if isinstance(latex_string, dict):
        for ls in latex_string.keys():
            latex_string[ls] = replace_variables(latex_string[ls], variable_map)
    elif isinstance(latex_string, list):
        for i in range(len(latex_string)):
            latex_string[i] = replace_variables(latex_string[i], variable_map)
    elif isinstance(latex_string, str):
        for old_name in variable_map.keys():
            try:
                latex_string = latex_string.replace(parse_latex(old_name), variable_map[old_name])
            except:
                latex_string = latex_string.replace(old_name, variable_map[old_name])
    return latex_string

def parse_latex(latex_str:str):
    """
    Converts a string into a LaTeX object

    Parameters:
    * `latex_str`: The LaTeX string

    Returns the LaTeX object
    """
    try:
        expression = parse_expr(latex_str, evaluate=False)
    except:
        return None
    latex_object = latex(expression, mul_symbol=' ')
    return latex_object

def equate_to(prepend:str, latex_string:str) -> str:
    """
    Performs a simple prepending

    Parameters:
    * `prepend`:      The string to prepend the larger string
    * `latex_string`: The larger LaTeX string

    Returns `{prepend} + " = " + {latex_string}`
    """
    return f"{prepend} = {latex_string}"

def equate_to_dict(latex_dict:dict) -> dict:
    """
    Prepends the keys to the values in the dict

    Parameters:
    * `latex_dict`: The dictionary of LaTeX strings

    Returns the dictionary with prepended values
    """
    for field in latex_dict.keys():
        latex_dict[field] = equate_to(field, latex_dict[field])
    return latex_dict

def process_str(base_str:str) -> str:
    """
    Removes spaces and newlines from a string,
    and replaces '^' with '**'

    Parameters:
    * `base_str`: The unprocessed string

    Returns the processed string
    """
    cleaned_str = str(base_str).replace(" ", "").replace("\n", "")
    processed_str = cleaned_str.replace("^", "**")
    return processed_str

def get_variables(expression:str) -> list:
    """
    Gets the variables from an expression

    Parameters:
    * `expression`: The expression string

    Returns a list of variables
    """
    expression = process_str(expression)
    try:
        expression = sympify(expression)
    except:
        return []
    variables = list(expression.free_symbols)
    return variables

def get_functions(expression:str) -> list:
    """
    Gets the functions from an expression

    Parameters:
    * `expression`: The expression string

    Returns a list of functions
    """
    expression = process_str(expression)
    expression = sympify(expression)
    functions = expression.find(lambda n: getattr(n, "is_Function", False))
    functions = [process_str(str(f)) for f in functions]
    return functions

def extract_julia(julia:str) -> dict:
    """
    Extracts information from a julia expression

    Parameters:
    * `julia`: The julia expression string

    Returns a dictionary of the julia information
    """

    # Initialise
    julia_clean = process_str(julia)
    julia_split = julia_clean.split(";")
    julia_dict = {}
    
    # Iterate through information
    for js in julia_split:

        # Extract name and value
        js_split = js.split("=")
        js_name = str(js_split[0])
        js_value = str(js_split[1])

        # Convert value if parameter
        if js_value.startswith("["):
            js_value_str = js_value[1:-1]
            js_value = [float(jsv) for jsv in js_value_str.split(",")]
            js_value = round_sf(js_value, 5)

        # Add information to dictionary
        julia_dict[js_name] = js_value

    # Return the dictionary
    return julia_dict

def save_latex(file_path:str, latex_equations:list) -> None:
    """
    Saves the plot and clears the figure

    Parameters:
    * `file_path`:      The path to save the plot
    * `latex_equation`: List/dict of equations in LaTeX
    """
    if not isinstance(latex_equations, list):
        latex_equations = [latex_equations]
    plt.figure(figsize=(8, 0.8 * len(latex_equations))) # adjust based on equations
    for idx, eq in enumerate(latex_equations):
        plt.text(0.5, 1 - (idx + 1) / (len(latex_equations) + 1), f"${eq}$", fontsize=18, ha="center", va="center")
    plt.axis("off")
    save_plot(file_path, {"bbox_inches": "tight"})

def set_parameters(combine_str:str, parameter_map:dict) -> str:
    """
    Sets parameter values in a combine string

    Parameters:
    * `combine_str`:   The combine string
    * `parameter_map`: Dictionary mapping parameter to value
    
    Returns the combine string with the set parameters
    """
    new_combine_str = combine_str
    for ph in parameter_map.keys():
        new_combine_str = new_combine_str.replace(ph, str(parameter_map[ph]))
    return new_combine_str

def julia_to_expression(julia:str, combine_str:str, final_str:str="f") -> dict:
    """
    Converts a julia expression to a latex string

    Parameters:
    * `julia`:       The julia expression string
    * `combine_str`: The combine string
    * `final_str`:   The name of the whole expression
    
    Returns a dictionary of latex strings
    """

    # Extract information from the julia expression
    julia_dict = extract_julia(julia)
    param_dict = {}
    function_dict = {}
    for definition in julia_dict.keys():
        if isinstance(julia_dict[definition], list):
            param_dict[definition] = julia_dict[definition]
        else:
            function_dict[definition] = julia_dict[definition]

    # Extract information from the combine string
    combine_str = process_str(combine_str)
    combine_split = combine_str.split(";")

    # Use julia information to fill combined expression
    combine_dict = {}
    for cs in combine_split:

        # If there is an '=', then it is a definition; otherwise, it is the final expression
        if "=" in cs:
            cs_split = cs.split("=")
            field = cs_split[0]
            expression = cs_split[1]
        else:
            field = final_str
            expression = cs

        # Replace all parameters
        for param_name in param_dict.keys():
            for i, param in enumerate(param_dict[param_name]):
                placeholder = f"{param_name}[{i+1}]"
                expression = expression.replace(placeholder, str(param))
        
        # Replace all functions
        functions = get_functions(expression)
        for f in functions:

            # Check if function has mapping
            function_handle = f.split("(")[0]
            if not function_handle in function_dict.keys():
                continue

            # Extract function information
            function_term = f"({function_dict[function_handle]})"
            function_variables = f.split("(")[1][:-1].split(",")

            # Replace placeholders
            for j, fv in enumerate(function_variables):
                function_term = function_term.replace(f"#{j+1}", fv)
            
            # Replace function in expression
            expression = expression.replace(f, function_term)
        
        # Add information to dictionary
        combine_dict[field] = expression
    
    # Return
    return combine_dict

def round_expression(expression_dict:dict, sf:int) -> str:
    """
    Rounds the numbers in an expression

    Parameters:
    * `expression_dict`: A dictionary of expressions; or just a string
    * `sf`:              What significant figures to round the numbers

    Returns the expression string with rounded numbers
    """

    # If dictionary, evaluate for each string
    if isinstance(expression_dict, dict):
        for field in expression_dict:
            expression_dict[field] = round_expression(expression_dict[field], sf)
        return expression_dict

    # If string, extract numbers potentially over the defined S.F.
    expression = expression_dict
    numbers = list(map(float, re.findall(r'[-+]?\d*\.?\d+|[-+]?\d+', expression)))
    numbers = [number for number in numbers if len(str(number)) > sf]

    # Round each number, replace, and return
    for number in numbers:
        rounded = round_sf(float(number), sf)
        expression = expression.replace(str(number), str(rounded))
    return expression

def expression_to_latex(expression_dict:dict) -> dict:
    """
    Converts a dictionary of expressions into
    a dictionary of LaTeX objects
    
    Parameters:
    * `expression`: The expression dictionary

    Returns the converted dictionary
    """
    expression_dict = deepcopy(expression_dict)
    for field in expression_dict.keys():
        expression = expression_dict[field]
        latex_expression = parse_latex(expression)
        expression_dict[field] = latex_expression
    expression_dict = equate_to_dict(expression_dict)
    return expression_dict

def replace_expression(expression:str, expression_dict:dict) -> float:
    """
    Replaces variables inside an expression

    Parameters:
    * `expression`:      The expression to undergo replacements
    * `expression_dict`: Dictionary of expressions
    
    The expression with replaced variables
    """

    # Iterate through variables
    has_replaced = False
    for expression_key in expression_dict:

        # Check if in expression
        pattern = rf'(?<![a-zA-Z0-9_]){re.escape(expression_key)}(?![a-zA-Z0-9_])'
        in_expression = re.search(pattern, expression) is not None
        
        # If in, then replace
        if in_expression:
            sub_expression = f"({expression_dict[expression_key]})"
            expression = expression.replace(expression_key, sub_expression)
            has_replaced = True
    
    # If have replaced, try again
    if has_replaced:
        expression = replace_expression(expression, expression_dict)
    
    # Return replaced expression
    return expression

def evaluate_expression(expression_dict:dict, target_field:str,
                        input_dict:dict, ignore_error:bool=False) -> float:
    """
    Evaluates an expression

    Parameters:
    * `expression_dict`: Dictionary of expressions
    * `target_field`:    The field of the expression to be evaluated
    * `input_dict`:      Dictionary of input values (lists)
    * `ignore_error`:    Whether to ignore errors in the eval;
                         If defined as a float, it replaces the evaluated
                         value with the float
    
    The result of the evaluation
    """

    # Get expression
    target_expression = expression_dict[target_field]
    target_expression = process_str(target_expression)
    target_expression = replace_expression(target_expression, expression_dict)
    
    # Evaluate the expression
    eval_values = []
    num_inputs = len(input_dict[list(input_dict.keys())[0]])
    for i in range(num_inputs):
        
        # Insert input variables
        eval_expression = target_expression
        for input_key in input_dict:
            input_value = f"({input_dict[input_key][i]})"
            eval_expression = eval_expression.replace(input_key, input_value)

        # Evaluate
        from math import exp, log, cos, cosh, sin, sinh, tan, tanh
        try:
            eval_value = eval(eval_expression)
            eval_values.append(eval_value)
        except ValueError as error:
            if isinstance(ignore_error, bool) and not ignore_error:
                raise error
            elif isinstance(ignore_error, float):
                eval_values.append(ignore_error)
    
    # Return evaluated values
    return eval_values
