"""
 Title:         The Controller class
 Description:   The intermediary between the interface and the rest of the code
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.constraints.__constraint__ import __Constraint__, create_constraint
from moga_neml.models.__model__ import __Model__, create_model
from moga_neml.errors.__error__ import __Error__
from moga_neml.io.plotter import Plotter, EXP_COLOUR, CAL_COLOUR, VAL_COLOUR
from moga_neml.io.boxplotter import plot_boxplots
from moga_neml.drivers.driver import Driver
from moga_neml.optimise.curve import Curve
from moga_neml.helper.experiment import get_labels_list
from moga_neml.helper.general import reduce_list, transpose

# Constants
MIN_DATA    = 5
BIG_VALUE   = 10000
ALL_COLOURS = ["red", "purple", "green", "orange", "blue", "magenta", "cyan", "olive", "pink", "brown"] * 10

# The Controller class
class Controller():

    def __init__(self):
        """
        Class to control all the components of the optimisation
        """
        
        # Initialise internal variables
        self.model           = None
        self.curve_list      = []
        self.constraint_list = []
        self.fix_param_dict  = {}
        self.init_param_dict = {}
        
        # Initialise variables for grouping errors
        self.group_name   = True
        self.group_type   = True
        self.group_labels = True
        
        # Initialise variables for reducing errors
        self.error_reduction_method     = "average"
        self.objective_reduction_method = "average"
        
    def define_model(self, model_name:str, **kwargs) -> None:
        """
        Defines the model

        Parameters:
        * `model_name`: The name of the model
        """
        self.model = create_model(model_name, **kwargs)
        
    def add_curve(self, exp_data:dict) -> None:
        """
        Adds an experimental curve to the controller
        
        Parameters:
        * `exp_data`: The corresponding experimental data
        """
        curve = Curve(exp_data, self.model)
        self.curve_list.append(curve)
    
    def get_curve_list(self) -> list:
        """
        Gets the list of curves
        """
        return self.curve_list
    
    def get_last_curve(self) -> Curve:
        """
        Returns the most recently added curve
        """
        if self.curve_list == []:
            raise ValueError("No curves have been added yet!")
        return self.curve_list[-1]

    def get_all_types(self) -> list:
        """
        Returns a list of all the types
        """
        type_list = [curve.get_type() for curve in self.curve_list]
        type_list = list(set(type_list))
        return type_list

    def get_param_names(self) -> list:
        """
        Returns a list of the model's parameter names
        """
        param_dict = self.model.get_param_dict()
        return list(param_dict.keys())

    def fix_param(self, param_name:str, param_value:float) -> None:
        """
        Fixes a parameter to a value

        Parameters:
        * `param_name`:  The name of the parameter
        * `param_value`: The value to fix the parameter to 
        """
        param_names = self.get_param_names()
        pretext = f"The '{param_name}' parameter cannot be fixed because"
        if not param_name in param_names:
            raise ValueError(f"{pretext} it is not defined in {self.model.get_name()}!")
        if param_name in self.init_param_dict.keys():
            raise ValueError(f"{pretext} it has already been set!")
        self.fix_param_dict[param_name] = param_value

    def init_param(self, param_name:str, param_value:float) -> None:
        """
        Sets the initial value of a parameter

        Parameters:
        * `param_name`:  The name of the parameter
        * `param_value`: The value to initialise the parameter to
        """
        param_names = self.get_param_names()
        pretext = f"The '{param_name}' parameter cannot be set because"
        if not param_name in param_names:
            raise ValueError(f"{pretext} it is not defined in {self.model.get_name()}!")
        if param_name in self.fix_param_dict.keys():
            raise ValueError(f"{pretext} it has already been fixed!")
        self.init_param_dict[param_name] = param_value

    def add_constraint(self, constraint_name:str, x_label:str="", y_label:str="", **kwargs) -> None:
        """
        Adds a constraint to the optimisation

        Parameters:
        * `constraint_name`: The name of the constraint to be added
        * `x_label`:         The label of the x axis
        * `y_label`:         The label of the y axis
        """
        
        # If constraint does not exist, create it
        constraint = self.get_constraint(constraint_name)
        if constraint == None:
            constraint = create_constraint(constraint_name, x_label, y_label, self.model, **kwargs)
            self.constraint_list.append(constraint)
        
        # Add the experimental data to it
        last_curve = self.get_last_curve()
        constraint.add_curve(last_curve)
    
    def get_constraint(self, constraint_name:str) -> __Constraint__:
        """
        Gets the constraint given a constraint name
        
        Parameters:
        * `constraint_name`: The name of the constraint to be added
        
        Returns the constraint if found, and nothing otherwise
        """
        for constraint in self.constraint_list:
            if constraint_name == constraint.get_name():
                return constraint

    def get_model(self) -> __Model__:
        """
        Returns the model
        """
        if self.model == None:
            raise ValueError("The model cannot be retrieved because it has not been defined yet!")
        return self.model

    def get_fix_param_dict(self) -> dict:
        """
        Gets information about the fixed parameters
        """
        return self.fix_param_dict

    def get_init_param_dict(self) -> dict:
        """
        Gets information about the initialised parameters
        """
        return self.init_param_dict

    def incorporate_fix_param_dict(self, *params:tuple) -> list:
        """
        Incorporates the fixed parameters

        Parameters:
        * `params`: The parameters
        """
        params = list(params)
        param_names = self.get_param_names()
        fix_indexes = [i for i in range(len(param_names)) if param_names[i] in self.fix_param_dict.keys()]
        for fix_index in fix_indexes:
            fix_value = self.fix_param_dict[param_names[fix_index]]
            params.insert(fix_index, fix_value)
        return tuple(params)

    def get_unfix_param_dict(self) -> dict:
        """
        Returns the information of unfixed parameters
        """
        unfix_param_dict = {}
        param_dict = self.model.get_param_dict()
        for param_name in param_dict.keys():
            if not param_name in self.fix_param_dict.keys():
                unfix_param_dict[param_name] = param_dict[param_name]
        return unfix_param_dict

    def get_unfix_param_names(self) -> list:
        """
        Returns a list of the unfixed parameters' named
        """
        unfix_param_dict = self.get_unfix_param_dict()
        unfix_param_names = list(unfix_param_dict.keys())
        return unfix_param_names

    def set_error_reduction_method(self, method:str):
        """
        Changes the reduction method for errors

        Parameters:
        * `method`: The reduction method for the errors to change to
        """
        self.error_reduction_method = method

    def get_error_reduction_method(self) -> str:
        """
        Gets the reduction method for errors
        """
        return self.error_reduction_method
      
    def set_objective_reduction_method(self, method:str):
        """
        Changes the reduction method for objective functions

        Parameters:
        * `method`: The reduction method for the objective functions to change to
        """
        self.objective_reduction_method = method

    def get_objective_reduction_method(self) -> str:
        """
        Gets the reduction method for objective functions
        """
        return self.objective_reduction_method

    def set_error_grouping(self, group_name:bool=True, group_type:bool=True, group_labels:bool=True) -> None:
        """
        Changes the variables for grouping the errors together

        Parameters:
        * `group_name`:   Whether to group the errors by name
        * `group_type:    Whether to group the errors by curve type
        * `group_labels`: Whether to group the errors by the curve labels
        """
        self.group_name = group_name
        self.group_type = group_type
        self.group_labels = group_labels

    def get_error_grouping(self) -> str:
        """
        Gets the error grouping approach as a string
        """
        group_str_list = [
            "name" if self.group_name else "",
            "type" if self.group_type else "",
            "labels" if self.group_labels else ""
        ]
        group_str_list = [group_str for group_str in group_str_list if group_str != ""]
        return ', '.join(group_str_list)

    def get_objective_info_list(self) -> list:
        """
        Returns information about the errors
        """
        objective_info_list = []
        for curve in self.curve_list:
            error_list = curve.get_error_list()
            for error in error_list:
                error_group_key = error.get_group_key(self.group_name, self.group_type, self.group_labels)
                objective_info_list.append(error_group_key)
        objective_info_list = list(set(objective_info_list))
        return objective_info_list

    def get_prd_data(self, curve:Curve, *params) -> dict:
        """
        Gets the predicted curve; returns none if the data is invalid

        Parameters:
        * `curve`:  The curve to predict
        * `params`: The parameters for the prediction

        Returns the predicted data
        """
        
        # Fix parameters and calibrate the model
        params = self.incorporate_fix_param_dict(*params)
        self.model.set_exp_data(curve.get_exp_data())
        calibrated_model = self.model.get_calibrated_model(*params)
        if calibrated_model == None:
            return None
        
        # Get the driver and prediction
        model_driver = Driver(curve, calibrated_model)
        prd_data = model_driver.run()

        # Check data has some data points
        if prd_data == None:
            return
        for field in prd_data.keys():
            if len(prd_data[field]) < MIN_DATA:
                return
        
        # Add the latest prediction to the curve and return the data
        curve.set_prd_data(prd_data)
        return prd_data
    
    def reduce_errors(self, error_list_dict:dict) -> dict:
        """
        Defines how the errors are reduced

        Parameters:
        * `error_list_dict`: A dictionary of error values

        Returns the reduced error values
        """
        objective_info_list = self.get_objective_info_list()
        error_value_dict = {}
        for error_info in objective_info_list:
            try:
                error_value_dict[error_info] = reduce_list(error_list_dict[error_info], self.error_reduction_method)
            except OverflowError:
                error_value_dict[error_info] = BIG_VALUE
        return error_value_dict
    
    def reduce_objectives(self, objective_list:list) -> float:
        """
        Defines how the objectives are reduced

        Parameters:
        * `objective_list`: The list of objective functions
        
        Returns the reduced objective value
        """
        try:
            return reduce_list(objective_list, self.objective_reduction_method)
        except OverflowError:
            return BIG_VALUE
    
    def calculate_objectives(self, *params, include_validation=False) -> dict:
        """
        Calculates the error values for a set of parameters

        Parameters:
        * `params`:             The parameters for the prediction
        * `include_validation`: Whether to include the validation data

        Returns a dictionary of the objectives
        """
        
        # Create a dictionary of errors
        objective_info_list = self.get_objective_info_list()
        empty_list_list = [[] for _ in range(len(objective_info_list))]
        error_list_dict = {key: value for key, value in zip(objective_info_list, empty_list_list)}
        
        # Initialise
        prd_data_list = []
        failed_dict = {key: value for key, value in zip(objective_info_list, [BIG_VALUE] * len(objective_info_list))}
        
        # Iterate through experimental data
        for curve in self.curve_list:
            
            # Ignore validation data
            error_list = curve.get_error_list()
            if len(error_list) == 0 and not include_validation:
                continue

            # Get prediction for training data
            prd_data = self.get_prd_data(curve, *params)
            if prd_data == None:
                return failed_dict

            # Gets all the errors and add to dictionary
            for error in error_list:
                error_value = error.get_value(prd_data)
                error_value = error_value * error.get_weight() if error_value != None else BIG_VALUE
                error_group_key = error.get_group_key(self.group_name, self.group_type, self.group_labels)
                error_list_dict[error_group_key].append(error_value)

        # Checks all the constraints
        for constraint in self.constraint_list:
            curve_list = constraint.get_curve_list()
            prd_data_list = [curve.get_prd_data() for curve in curve_list if len(curve.get_error_list()) > 0]
            if not constraint.check(prd_data_list):
                return failed_dict
        
        # Reduce and return errors
        objective_dict = self.reduce_errors(error_list_dict)
        return objective_dict

    def plot_exp_curves(self, type:str, file_path:str="", x_log:bool=False, y_log:bool=False) -> None:
        """
        Plots the experimental curves for a given type

        Parameters:
        * `type:`       The type of the experimental data
        * `file_path`:  The path to plot the experimental curves without the extension
        * `x_log`:      Whether to log the x axis
        * `y_log`:      Whether to log the y axis
        """

        # Gets the data of defined type
        curve_list = [curve for curve in self.curve_list if curve.get_type() == type]
        
        # Iterate through data field combinations
        labels_list = get_labels_list(type)
        for x_label, y_label in labels_list:

            # Prepare the plotter
            plot_file_path = f"{file_path}_{x_label}_{y_label}.png"
            plotter = Plotter(plot_file_path, x_label, y_label)
            plotter.prep_plot("Experimental")
            
            # Plot the data
            for curve in curve_list:
                plotter.scat_plot(curve.get_exp_data(), colour=EXP_COLOUR)

            # Format, save, and clear for next plot
            plotter.set_log_scale(x_log, y_log)
            plotter.define_legend(["gray"], ["Used Data"], [7], ["scatter"])
            plotter.save_plot()
            plotter.clear()

    def plot_prd_curves(self, params_list:list, alpha_list:list, clip:bool, type:str, file_path:str="", 
                        x_limits:float=None, y_limits:float=None) -> None:
        """
        Visualises the predicted curves from a set of parameters
        
        Parameters:
        * `params_list`: A list of parameter values of the model
        * `alpha_list`:  A list of alpha values for the plots
        * `clip`:        Whether to clip the predictions so they end at the same x position as the
        * `type:`        The type of the experimental data
        * `file_path`:   The path to plot the experimental curves without the extension
                         experimental data
        * `x_limits`:    The upper and lower bounds of the plot for the x scale
        * `y_limits`:    The upper and lower bounds bound of the plot for the y scale
        """

        # Get predicted curves first
        typed_curve_list = [curve for curve in self.curve_list if curve.get_type() == type]
        prd_data_list_list = []
        for params in params_list:
            prd_data_list = []
            for curve in typed_curve_list:
                prd_data = self.get_prd_data(curve, *params)
                if prd_data == None:
                    raise ValueError(f"The model is unable to run with the parameters - {params}!")
                prd_data_list.append(prd_data)
            prd_data_list_list.append(prd_data_list)

        # Iterate through data field combinations
        labels_list = get_labels_list(type)
        for x_label, y_label in labels_list:

            # Prepare the plotter
            plot_file_path = f"{file_path}_{x_label}_{y_label}.png"
            plotter = Plotter(plot_file_path, x_label, y_label)
            plotter.prep_plot(f"Experimental vs Simulation ({type.capitalize()})")
            plotter.set_limits(x_limits, y_limits)
            
            # Plot experimental data
            for curve in typed_curve_list:
                exp_data = curve.get_exp_data()
                plotter.scat_plot(exp_data, size=7, colour=EXP_COLOUR)

            # Plot predictions
            for j in range(len(params_list)):
                for k in range(len(typed_curve_list)):
                    colour = VAL_COLOUR if typed_curve_list[k].is_validation() else CAL_COLOUR
                    # colour = ALL_COLOURS[j]
                    prd_data = prd_data_list_list[j][k]
                    if clip:
                        max_x = max(typed_curve_list[k].get_exp_data()[x_label])
                        x_list = [x_value for x_value in prd_data[x_label] if x_value <= max_x]
                        prd_data[y_label] = [prd_data[y_label][j] for j in range(len(prd_data[x_label]))
                                            if prd_data[x_label][j] <= max_x]
                        prd_data[x_label] = x_list
                    plotter.line_plot(prd_data, colour, linewidth=3, alpha=alpha_list[j])

            # Define legend information
            has_valid   = True in [curve.is_validation() for curve in typed_curve_list]
            colour_list = [EXP_COLOUR, CAL_COLOUR, VAL_COLOUR] if has_valid else [EXP_COLOUR, CAL_COLOUR]
            label_list  = ["Experimental", "Calibration", "Validation"] if has_valid else ["Experimental", "Calibration"]
            size_list   = [7, 2.5, 2.5] if has_valid else [7, 2.5]
            type_list   = ["scatter", "line", "line"] if has_valid else ["scatter", "line"]

            # Format and save the plot
            plotter.define_legend(colour_list, label_list, size_list, type_list)
            plotter.save_plot()
            plotter.clear()

    def plot_distribution(self, params_list:list, file_path:str, limits_dict:dict=None, log:bool=False,
                          horizontal:bool=True) -> None:
        """
        Visualises the distribution of parameters
        
        Parameters:
        * `params_list`:   A list of parameter sets for the model; note that defining the parameters as
                           arguments to this function is similar to fixing the parameters via `fix_params`,
                           meaning that there will be clashes if the parameter values are defined twice.
        * `file_path`:     The path to save the boxplots
        * `limits_dict`:   A dictionary of tuples (i.e., (lower, upper)) defining the scale for each parameter
        * `log`:           Whether to apply log scale or not
        * `horizontal`:    Whether to plot the boxplots horizontally (or vertically)
        """
        params_list = transpose(params_list)
        plot_boxplots(params_list, file_path, "Distribution of parameters", ALL_COLOURS, limits_dict, log, horizontal)
