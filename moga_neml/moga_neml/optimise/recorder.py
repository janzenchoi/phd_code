"""
 Title:         Recorder
 Description:   For recording results periodically
 Author:        Janzen Choi

"""

# Libraries
import time
from copy import deepcopy
from moga_neml.io.plotter import Plotter, EXP_COLOUR, CAL_COLOUR, VAL_COLOUR
from moga_neml.io.spreadsheet import Spreadsheet
from moga_neml.helper.data import  get_thinned_list
from moga_neml.helper.experiment import get_labels_list
from moga_neml.optimise.controller import Controller
from moga_neml.helper.general import get_file_path_writable, get_file_path_exists

# The Recorder class
class Recorder:
    
    def __init__(self, controller:Controller, interval:int, results_dir:str,
                 plot_opt:bool=False, plot_loss:bool=False, save_model:bool=False):
        """
        Class for recording the results

        Parameters:
        * `controller`:  The controller for controlling the optimisation results
        * `interval`:    The number of generations to record the results
        * `results_dir`: The directory to store the results
        * `plot_opt`:    Whether to plot the best plot after every update
        * `plot_loss`:   Whether to plot the loss history after every update
        * `save_model`:  Whether to save the best calibrated model
        """
        
        # Initialise inputs
        self.controller  = controller
        self.interval    = interval
        self.results_dir = results_dir
        self.plot_opt    = plot_opt
        self.plot_loss   = plot_loss
        self.save_model  = save_model
        
        # Initialise internal variables
        self.curve_list          = controller.get_curve_list()
        self.num_evals_completed = 0
        self.num_gens_completed  = 0
        self.start_time          = time.time()
        self.update_time         = self.start_time
        self.start_time_str      = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        
        # Get parameter information
        param_dict      = self.controller.get_model().get_param_dict()
        fix_param_dict  = self.controller.get_fix_param_dict()
        init_param_dict = self.controller.get_init_param_dict()
        
        # Summarise parameter information
        self.param_info_list = []
        for param_name in param_dict.keys():
            param_info = param_name
            if param_name in fix_param_dict.keys():
                param_info += " (fixed={:0.4})".format(float(fix_param_dict[param_name]))
            elif param_name in init_param_dict.keys():
                param_info += " (init={:0.4})".format(float(init_param_dict[param_name]))
            self.param_info_list.append(param_info)
        
        # Summarise parameter bound information
        self.param_bound_info_list = []
        for param_name in param_dict.keys():
            l_bound = float(param_dict[param_name]["l_bound"])
            u_bound = float(param_dict[param_name]["u_bound"])
            self.param_bound_info_list.append("[{:0.4}, {:0.4}]".format(l_bound, u_bound))
        
        # Summarise data information
        self.data_info_list = []
        for curve in self.curve_list:
            status = "Validation" if curve.is_validation() else "Calibration"
            data_info = "{} ({})".format(curve.get_exp_data()["file_name"], status)
            self.data_info_list.append(data_info)
        
        # Summarise grouping / reduction methods
        self.reduction_method_list = [
            f"Grouping Errors ({self.controller.get_error_grouping()})",
            f"Reducing Errors ({self.controller.get_error_reduction_method()})",
            f"Reducing Objectives ({self.controller.get_objective_reduction_method()})",
        ]
        
        # Initialise optimal solution
        self.optimal_prd_data = None
        self.optimal_solution_list = []
        self.loss_history = {"generations": [], "loss": []}
    
    def define_hyperparameters(self, num_gens:int, population:int, offspring:int,
                               crossover:float, mutation:float) -> None:
        """
        Define MOGA hyperparameters

        Parameters:
        * `num_gens`:   The number of generations to run the optimiser
        * `population`: The size of the initial population
        * `offspring`:  The size of the offspring
        * `crossover`:  The crossover probability
        * `mutation`:   The mutation probability
        """
        self.num_gens   = num_gens
        self.population = population
        self.offspring  = offspring
        hp_names        = ["num_gens", "population", "offspring", "crossover", "mutation"]
        hp_values       = [num_gens, population, offspring, crossover, mutation]
        self.moga_summary = [f"{hp_names[i]} ({hp_values[i]})" for i in range(len(hp_names))]
    
    def update_optimal_solution(self, param_dict:dict, objective_dict:dict) -> None:
        """
        Updates the population

        Parameters:
        * `param_dict`:     The dictionary of parameters
        * `objective_dict`: The dictionary of objective functions
        """

        # Get the solution
        reduction_method = self.controller.get_objective_reduction_method()
        objective_values = list(objective_dict.values())
        reduced_value    = self.controller.reduce_objectives(objective_values)
        solution         = {"params": param_dict, "objectives": objective_dict, reduction_method: reduced_value}
        
        # If the stored parameters exceed the limit, remove the worst
        if len(self.optimal_solution_list) == self.population:
            if self.optimal_solution_list[-1][reduction_method] < solution[reduction_method]:
                return
            self.optimal_solution_list.pop()

        # Adds new solution in order
        for i in range(len(self.optimal_solution_list)):
            if solution[reduction_method] < self.optimal_solution_list[i][reduction_method]:
                self.optimal_solution_list.insert(i, solution)
                return
        self.optimal_solution_list.append(solution)
    
    def update_iteration(self, param_dict:dict, objective_dict:dict) -> None:
        """
        Updates the results after a MOGA iteration
        
        Parameters:
        * `param_dict`:     The dictionary of parameters
        * `objective_dict`: The dictionary of objective functions
        """

        # Print separating line if initial update
        if self.num_evals_completed == 0:
            print()

        # Update optimisation progress
        self.num_evals_completed += 1
        self.num_gens_completed = (self.num_evals_completed - self.population) / self.offspring + 1
        self.update_optimal_solution(param_dict, objective_dict)
        
        # Record results after X generations
        if self.num_gens_completed > 0 and self.num_gens_completed % self.interval == 0:
            self.record_results()

    def record_results(self) -> None:
        """
        Updates the results after X MOGA iterations
        """

        # Get time since previous update in seconds
        current_time = time.time()
        update_duration = round(current_time - self.update_time)
        self.update_time = current_time

        # Display output
        num_gens_completed_padded = str(round(self.num_gens_completed)).zfill(len(str(self.num_gens)))
        self.create_record(f"{self.results_dir}/results")

        # Display progress in console
        progress = f"{num_gens_completed_padded}/{self.num_gens}"
        index = round(self.num_gens_completed//self.interval)
        print(f"      {index}]\tRecorded in {update_duration}s ({progress} gens, {self.num_evals_completed} evals)")
    
    def get_summary_dict(self) -> dict:
        """
        Gets the optimisation summary;
        returns the dictionary
        """
        return {
            "Progress":     [f"{round(self.num_gens_completed)}/{self.num_gens}"],
            "Start / End":  [self.start_time_str, time.strftime("%A, %D, %H:%M:%S", time.localtime())],
            "Model":        [self.controller.get_model().get_name()],
            "Params":       self.param_info_list,
            "Bounds":       self.param_bound_info_list,
            "Experimental Data": self.data_info_list,
            "Objectives":   self.controller.get_objective_info_list(),
            "MOGA Summary": self.moga_summary,
            "Reduction":    self.reduction_method_list,
        }
    
    def get_result_dict(self) -> dict:
        """
        Gets a dictionary of the optimisation results;
        returns the dictionary of results
        """

        # Initialise
        results = {}
        sf_format = lambda x : float("{:0.5}".format(float(x)))
        
        # Get parameter information
        fix_params = self.controller.get_fix_param_dict()
        all_param_names = self.controller.get_param_names()
        for param_name in all_param_names:
            if param_name in fix_params.keys():
                results[param_name] = [sf_format(fix_params[param_name]) for _ in self.optimal_solution_list]
            else:
                results[param_name] = [sf_format(o_sol["params"][param_name]) for o_sol in self.optimal_solution_list]

        # Add objective information
        objective_info_list = self.controller.get_objective_info_list()
        for objective_info in objective_info_list:
            results[objective_info] = [sf_format(o_sol["objectives"][objective_info]) for o_sol in self.optimal_solution_list]
        
        # Reduce objective values and return
        reduction_method = self.controller.get_objective_reduction_method()
        results[reduction_method] = [sf_format(o_sol[reduction_method]) for o_sol in self.optimal_solution_list]
        return results
    
    def get_opt_params(self) -> dict:
        """
        Returns the best set of parameters from the optimisation
        """
        return self.optimal_solution_list[0]["params"]

    def get_opt_error(self) -> float:
        """
        Returns the error corresponding to the best set of parameters from the optimisation
        """
        reduction_method = self.controller.get_objective_reduction_method()
        return self.optimal_solution_list[0][reduction_method]

    def get_plot_dict(self, prd_data_list:list, typed_curve_list:list, x_label:str, y_label:str) -> dict:
        """
        Gets the curves for a curve type

        Parameters:
        * `prd_data_list`:    The list of predicted data
        * `typed_curve_list`: The list of relevant experimental curves
        * `x_label`:          The label of the x axis
        * `y_label`:          The label of the y axis

        Returns the dictionary of plot information, and none if the predicted data is invalid
        """
        
        # Initialise data structure
        calib_dict = {"exp_x": [], "exp_y": [], "prd_x": [], "prd_y": []}
        valid_dict = {"exp_x": [], "exp_y": [], "prd_x": [], "prd_y": []}
        
        # Iterate through curves and predictions
        for i in range(len(prd_data_list)):

            # Get experimental / predicted data and process
            exp_data = typed_curve_list[i].get_exp_data()
            prd_data = prd_data_list[i]
            exp_x_list, exp_y_list = process_data_dict(exp_data, x_label, y_label)
            prd_x_list, prd_y_list = process_data_dict(prd_data, x_label, y_label)
            
            # Add to data structure
            data_dict = valid_dict if typed_curve_list[i].is_validation() else calib_dict
            data_dict["exp_x"] += exp_x_list
            data_dict["exp_y"] += exp_y_list
            data_dict["prd_x"] += prd_x_list
            data_dict["prd_y"] += prd_y_list

        # Prepare dict for plotting data
        plot_dict = {}
        plot_dict["Experimental"] = {x_label: calib_dict["exp_x"] + valid_dict["exp_x"],
                                     y_label: calib_dict["exp_y"] + valid_dict["exp_y"],
                                     "size": 5, "colour": "gray"}
        if False in [curve.is_validation() for curve in typed_curve_list]:
            plot_dict["Calibration"] = {x_label: calib_dict["prd_x"], y_label: calib_dict["prd_y"],
                                        "size": 2, "colour": "green"}
        if True in [curve.is_validation() for curve in typed_curve_list]:
            plot_dict["Validation"] = {x_label: valid_dict["prd_x"], y_label: valid_dict["prd_y"],
                                       "size": 2, "colour": "red"}
        return plot_dict

    def get_plot_dict_list(self, type:str) -> list:
        """
        Gets a list of plot data information based on the data type

        Parameters:
        * `type`: The type of data to be plotted

        Returns a list of plot data dictionaries
        """

        # Get predicted curves first
        opt_params = self.get_opt_params().values()
        typed_curve_list = [curve for curve in self.curve_list if curve.get_type() == type]
        prd_data_list = []
        for curve in typed_curve_list:
            prd_data = self.controller.get_prd_data(curve, *opt_params)
            if prd_data == None:
                return
            prd_data_list.append(prd_data)

        # Iterate through data field combinations and return the list
        plot_dict_list = []
        labels_list = get_labels_list(type)
        for x_label, y_label in labels_list:
            plot_dict = self.get_plot_dict(prd_data_list, typed_curve_list, x_label, y_label)
            plot_dict_list.append(plot_dict)
        return plot_dict_list

    def create_record(self, file_path:str, replace:bool=True) -> None:
        """
        Returns a writer object

        Parameters:
        * `file_path`:  The path to the record without the extension
        * `replace`:    Whether to replace the results file or not
        """

        # If no optimal solutions, leave
        if len(self.optimal_solution_list) == 0:
            return

        # Output something from the model if implemented
        opt_params = self.get_opt_params().values()
        all_params = self.controller.incorporate_fix_param_dict(*opt_params)
        self.controller.get_model().record_results(self.results_dir, *all_params)

        # Get the plot data
        plot_dict_list_dict = {}
        for type in self.controller.get_all_types():
            plot_dict_list = self.get_plot_dict_list(type)
            if plot_dict_list == None:
                return
            plot_dict_list_dict[type] = plot_dict_list

        # Create the spreadsheet and write to it
        file_path = get_file_path_writable(file_path, "xlsx") if replace else get_file_path_exists(file_path, "xlsx")
        spreadsheet = Spreadsheet(file_path)
        spreadsheet.write_data(self.get_summary_dict(), "summary")
        spreadsheet.write_data(self.get_result_dict(), "results")
        for type in self.controller.get_all_types():
            labels_list = get_labels_list(type)
            for i in range(len(labels_list)):
                x_label, y_label = labels_list[i]
                plot_dict = deepcopy(plot_dict_list_dict[type][i])
                sheet_name = f"plot_{type}_{x_label}_{y_label}"
                if x_label == "time":
                    for data_type in plot_dict.keys():
                        plot_dict[data_type][x_label] = [x/3600 for x in plot_dict[data_type][x_label]]
                spreadsheet.write_plot(plot_dict, sheet_name, x_label, y_label, "scatter")
        spreadsheet.close()
    
        # Creates a quick-view plot, if desired
        if self.plot_opt:
            for type in self.controller.get_all_types():
                labels_list = get_labels_list(type)
                for i in range(len(labels_list)):
                    x_label, y_label = labels_list[i]
                    plot_dict = plot_dict_list_dict[type][i]
                    plotter = Plotter(f"{self.results_dir}/opt_{type}_{x_label}_{y_label}.png", x_label, y_label)
                    plotter.prep_plot("Best Simulation")
                    for key in plot_dict.keys():
                        plotter.scat_plot(plot_dict[key], plot_dict[key]["colour"], plot_dict[key]["size"])
                    
                # Define legend information
                has_valid   = True in ["Validation" in plot_dict.keys() for plot_dict in plot_dict_list_dict[type]]
                colour_list = [EXP_COLOUR, CAL_COLOUR, VAL_COLOUR] if has_valid else [EXP_COLOUR, CAL_COLOUR]
                label_list  = ["Experimental", "Calibration", "Validation"] if has_valid else ["Experimental", "Calibration"]
                size_list   = [7, 1.5, 1.5] if has_valid else [7, 1.5]
                type_list   = ["scatter", "line", "line"] if has_valid else ["scatter", "line"]

                # Format and save the plot
                plotter.define_legend(colour_list, label_list, size_list, type_list)
                plotter.save_plot()
                plotter.clear()

        # Output files based on recorder settings
        self.write_error() if self.plot_opt else None
        self.write_loss() if self.plot_loss else None
        self.save_calibrated_model() if self.save_model else None

    def write_error(self):
        """
        Creates a text file with the reduced error
        """
        reduced_error = self.get_opt_error()
        reduced_error_path = get_file_path_writable(f"{self.results_dir}/opt_err", "txt")
        with open(reduced_error_path, "w+") as fh:
            fh.write(str(reduced_error))

    def write_loss(self):
        """
        Creates a text file with the loss history and creates a plot
        """

        # Get loss data
        reduction_method = self.controller.get_objective_reduction_method()
        loss = self.optimal_solution_list[-1][reduction_method]
        self.loss_history["loss"].append(round(loss, 6))
        self.loss_history["generations"].append(self.num_gens_completed)

        # Format loss data and write it
        loss_path = get_file_path_writable(f"{self.results_dir}/opt_loss", "csv")
        loss_history_str = "\n".join([f"{self.loss_history['generations'][i]}, {self.loss_history['loss'][i]}"
                                        for i in range(len(self.loss_history["loss"]))])
        with open(loss_path, "w+") as fh:
            fh.write(loss_history_str)

        # Plot loss
        plotter = Plotter(f"{self.results_dir}/opt_loss.png", "generations", "loss")
        plotter.prep_plot("Loss history")
        plotter.set_log_scale(False, True)
        plotter.scat_plot(self.loss_history, "red", 3)
        plotter.save_plot()
        plotter.clear()

    def save_calibrated_model(self, custom_params:tuple=None):
        """
        Saves the calibrated model

        Parameters:
        * `custom_params`: Parameters as a list; if undefined, uses the most optimal
                           parameters from the optimisation
        """

        # Iterate through all experimental data
        curve_list = self.controller.get_curve_list()
        for i in range(len(curve_list)):

            # Sets the experimental data to the curve
            exp_data = curve_list[i].get_exp_data()
            self.controller.model.set_exp_data(exp_data)

            # Get calibrated model
            params = self.get_opt_params().values() if custom_params == None else custom_params
            params = self.controller.incorporate_fix_param_dict(*params)
            calibrated_model = self.controller.model.get_calibrated_model(*params)
            
            # Saves the model
            model_path = get_file_path_writable(f"{self.results_dir}/opt_model_{i+1}", "xml")
            model_name = self.controller.model.get_name()
            calibrated_model.save(model_path, model_name)

def process_data_dict(data_dict:dict, x_label:str, y_label:str) -> tuple:
    """
    For thinning data

    Parameters:
    * `data_dict`: The dictionary of data
    * `x_label`:   The label of the x axis
    * `y_label`:   The label of the y axis

    Returns the thinned x and y lists
    """
    data_dict[x_label] = get_thinned_list(data_dict[x_label], 1000)
    data_dict[y_label] = get_thinned_list(data_dict[y_label], 1000)
    return data_dict[x_label], data_dict[y_label]
