"""
 Title:         Recorder
 Description:   For recording results periodically
 Author:        Janzen Choi

"""

# Libraries
import time
from opt_all.helper.general import dict_to_csv, get_file_path_writable
from opt_all.io.plotter import Plotter, CAL_COLOUR, EXP_COLOUR, VAL_COLOUR

# The Recorder class
class Recorder:

    def __init__(self, controller, output_path:str, storage:int,
                 interval:int, export:bool, verbose:bool) -> None:
        """
        Initialises the recorder class

        Parameters:
        * `controller`:  The controller object
        * `output_path`: The path to the output directory
        * `storage`:     The number of solutions to store
        * `interval`:    The number of evaluations for each record
        * `export`:      Whether to export data during recording or not
        * `verbose`:     Whether to output the recording progress
        """

        # Define input parameters
        self.controller  = controller
        self.output_path = output_path
        self.storage     = storage
        self.interval    = interval
        self.export      = export
        self.verbose     = verbose

        # Define internal parameters
        self.num_evals    = 0
        self.update_time  = time.time()
        self.solutions    = []
        self.loss_history = {"evals": [], "errors": []}
        self.sf_5 = lambda x : float("{:0.5}".format(float(x)))

        # Sets up storage
        self.plot_records = []

    def update(self, params:list, errors:list) -> None:
        """
        Updates the records

        Parameters:
        * `params`: A list of parameters
        * `errors`: The corresponding list of errors
        """

        # Update number of evaluations and output results if necessary
        self.num_evals += 1
        if self.num_evals % self.interval == 0:

            # Display message
            if self.verbose:
                duration = round(time.time() - self.update_time)
                print(f"    {self.num_evals // self.interval}]  \tRecording ({self.num_evals} evals, {duration} seconds)")
                self.update_time = time.time()

            # Update loss history
            self.loss_history["evals"].append(self.num_evals)
            self.loss_history["errors"].append(self.solutions[0]["reduced"])

            # Outputs the results
            self.output_results()

        # Format inputs
        reduced_error = self.controller.reduce_errors(errors)
        params = [self.sf_5(param) for param in params]
        errors = [self.sf_5(error) for error in errors]
        solution = {"params": params, "errors": errors, "reduced": reduced_error}

        # # Append solutions
        # if len(self.solutions) == self.storage:
        #     self.solutions = self.solutions[1:]
        # self.solutions.append(solution)

        # If the worst stored solution is worse than the new solution, remove it
        if len(self.solutions) == self.storage:
            if self.solutions[-1]["reduced"] < solution["reduced"]:
                return
            self.solutions.pop()

        # Adds new solution in order
        for i in range(len(self.solutions)):
            if self.solutions[i]["reduced"] > solution["reduced"]:
                self.solutions.insert(i, solution)
                return
        self.solutions.append(solution)

    def output_results(self) -> None:
        """
        Outputs the results to the defined output path
        """
        if self.solutions == []:
            return
        self.export_summary()
        self.export_loss()
        self.export_data()
        self.export_plot()
        self.run_custom_function()

    def export_summary(self) -> None:
        """
        Creates a summary file
        """

        # Add parameters to summary dict
        summary_dict = {}
        param_names = self.controller.model.get_param_names()
        for i in range(len(param_names)):
            param_values = [solution["params"][i] for solution in self.solutions]
            summary_dict[f"Param ({param_names[i]})"] = param_values
        
        # Add errors to summary dict
        error_groups = self.controller.get_error_groups()
        for i in range(len(error_groups)):
            error_values = [solution["errors"][i] for solution in self.solutions]
            summary_dict[f"Error ({error_groups[i]})"] = error_values
        
        # Add reduced errors to summary dict and write
        summary_dict["Reduced Error"] = [solution["reduced"] for solution in self.solutions]
        summary_path = get_file_path_writable(f"{self.output_path}/params", "csv")
        dict_to_csv(summary_dict, summary_path)

    def export_loss(self) -> None:
        """
        Creates plot for the loss history
        """

        # Save loss history to a file
        loss_path = get_file_path_writable(f"{self.output_path}/loss", "csv")
        dict_to_csv(self.loss_history, loss_path)

        # Plot loss history
        loss_path = get_file_path_writable(f"{self.output_path}/loss", "png")
        plotter = Plotter(loss_path, "evals", "errors")
        plotter.prep_plot("Loss history")
        plotter.scat_plot(self.loss_history)
        plotter.save_plot()
        plotter.clear()

    def export_data(self) -> None:
        """
        Exports data
        """

        # Ignore if not specified
        if not self.export:
            return

        # Initialise
        curve_list = self.controller.get_curve_list()
        opt_params = self.solutions[0]["params"]

        # Iterate through curves
        for i, curve in enumerate(curve_list):
            
            # Prepare data
            exp_data = curve.get_exp_data()
            sim_data = {}
            for field in exp_data.keys():
                if not isinstance(exp_data[field], list):
                    sim_data[field] = exp_data[field]
            res_data = self.controller.get_response(*opt_params, curve=curve)
            sim_data = {**sim_data, **res_data}

            # Get export path
            output_path = f"{self.output_path}/data_{i+1}"
            output_path = get_file_path_writable(output_path, "csv")

            # Export data
            dict_to_csv(sim_data, output_path)

    def add_plot_record(self, x_field:str, y_field:str, x_units:str="", x_scale:float=1.0,
                        y_scale:float=1.0, y_units:str="", x_limits:tuple=None,
                        y_limits:tuple=None, file_path:str="", conditions:dict={}) -> None:
        """
        Sets up plots for the fitting results during recording

        Parameters:
        * `x_field`:    Field to use for the x-axis
        * `y_field`:    Field to use for the y-axis
        * `x_scale`:    Factor to apply to x values
        * `y_scale`:    Factor to apply to y values
        * `x_limits`:   Limits to apply on the x-axis
        * `y_limits`:   Limits to apply on the y-axis
        * `file_path`:  Custom name for the plot file
        * `conditions`: Conditions to constrain plotting
        """
        plot_record = {
            "x_field":    x_field,
            "y_field":    y_field,
            "x_units":    x_units,
            "x_scale":    x_scale,
            "y_scale":    y_scale,
            "y_units":    y_units,
            "x_limits":   x_limits,
            "y_limits":   y_limits,
            "file_path":  file_path,
            "conditions": conditions,
        }
        self.plot_records.append(plot_record)

    def export_plot(self) -> None:
        """
        Creates plots for defined labels
        """

        # Initialise
        all_curve_list = self.controller.get_curve_list()
        opt_params = self.solutions[0]["params"]

        # Iterate through plot records
        for plot_record in self.plot_records:

            # Identify relevant curves
            plot_curve_list = []
            for curve in all_curve_list:

                # Check fields                
                if (not curve.has_field(plot_record["x_field"]) or
                    not curve.has_field(plot_record["y_field"])):
                    continue

                # Check conditions
                conditions = plot_record["conditions"]
                satisfied = True
                for field in conditions.keys():
                    if not curve.has_data(field, conditions[field]):
                        satisfied = False
                
                # Plot curve if fields and conditions satisfied
                if satisfied:
                    plot_curve_list.append(curve)

            # Prepare plotter
            plot_path = get_file_path_writable(plot_record["file_path"], "png")
            plotter = Plotter(plot_path, plot_record["x_field"], plot_record["y_field"])
            plotter.prep_plot()

            # Iterate through curves
            for curve in plot_curve_list:
                
                # Plot experimental data
                exp_dict = curve.get_exp_data()
                plotter.scat_plot(exp_dict, EXP_COLOUR, 8, 3)

                # Plot simulation data
                colour = VAL_COLOUR if curve.is_validation() else CAL_COLOUR
                sim_dict = self.controller.get_response(*opt_params, curve=curve)
                plotter.line_plot(sim_dict, colour, 3, 4)
    
            # Format and save
            plotter.define_legend(
                colour_list = [EXP_COLOUR, CAL_COLOUR, VAL_COLOUR],
                label_list  = ["Experimental", "Calibration", "Validation"],
                size_list   = [8, 3, 3],
                type_list   = ["scatter", "line", "line"]
            )
            plotter.save_plot()
            plotter.clear()

    def run_custom_function(self) -> None:
        """
        Runs functions for each curve
        """

        # Iterate through curves
        curve_list = self.controller.get_curve_list()
        for curve in curve_list:

            # Check if any functions to run
            function_list = curve.get_function_list()
            if len(function_list) == 0:
                continue

            # Get data
            exp_dict = curve.get_exp_data()
            opt_params = self.solutions[0]["params"]
            sim_dict   = self.controller.get_response(*opt_params, curve=curve)

            # Run function
            for function in function_list:
                function(exp_dict, sim_dict, self.output_path)
