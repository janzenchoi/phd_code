"""
 Title:         Controller
 Description:   Directs the symbolic regression procedure
 Author:        Janzen Choi

"""

# Libraries
import matplotlib.pyplot as plt
from symbolic.io.dataset import Dataset
from symbolic.io.files import dict_to_csv
from symbolic.helper.general import get_thinned_list, flatten
from symbolic.helper.plotter import prep_plot, set_limits, add_legend, save_plot
from symbolic.helper.plotter import create_1to1, plot_1to1
from symbolic.helper.plotter import EXP_COLOUR, CAL_COLOUR, VAL_COLOUR
from symbolic.regression.expression import save_latex
from symbolic.models.__model__ import get_model
from copy import deepcopy

# Controller class
class Controller:

    def __init__(self, output_path:str):
        """
        Constructor for the controller class

        Parameters:
        * `output_path`:   Path to the output directory
        """
        self.output_path = output_path
        self.model = None
        self.data_list = []
    
    def define_model(self, model_name:str, **kwargs) -> None:
        """
        Defines the model

        Parameters:
        * `model_name`: Name of the model
        """
        self.model = get_model(model_name, self.output_path, **kwargs)

    def add_data(self, csv_path:str, fitting:bool=True) -> None:
        """
        Adds fitting data

        Parameters:
        * `csv_path`: Path to the csv file containing the data
        * `fitting`:  Whether the data will be used for fitting
        """
        data = Dataset(csv_path, fitting)
        self.data_list.append(data)

    def sparsen_data(self, new_size:int=100) -> None:
        """
        Sparsen the most recently added dataset

        Parameters:
        * `new_size`: New size to sparsen the data to
        """
        last_data = self.get_last_data()
        last_data_dict = last_data.get_data_dict()
        for field in last_data_dict.keys():
            if isinstance(last_data_dict[field], list):
                last_data_dict[field] = get_thinned_list(last_data_dict[field], new_size)
        last_data.set_data_dict(last_data_dict)
        self.set_last_data(last_data)

    def change_data(self, function_handler) -> None:
        """
        Uses a function to change the data;
        the function should take in a dictionary and return a dictionary

        Parameters:
        * `function_handle`: The function handle
        """
        last_data = self.get_last_data()
        last_data_dict = last_data.get_data_dict()
        last_data_dict = function_handler(last_data_dict)
        last_data.set_data_dict(last_data_dict)
        self.set_last_data(last_data)

    def change_field(self, field:str, function_handler) -> None:
        """
        Uses a function to change the values in a field;
        the function should take in a list/float and return
        a list/float

        Parameters:
        * `field`:           The field to change
        * `function_handle`: The function handle
        """
        last_data = self.get_last_data()
        last_data_dict = last_data.get_data_dict()
        last_data_dict[field] = function_handler(last_data_dict[field])
        last_data.set_data_dict(last_data_dict)
        self.set_last_data(last_data)

    def set_weight(self, weight:float) -> None:
        """
        Sets the weight to the most recently added dataset

        Parameters:
        * `weight`: Weight of dataset relative to other datasets
        """
        last_data = self.get_last_data()
        last_data.set_weight(weight)
        self.set_last_data(last_data)

    def set_weights(self, weights:list) -> None:
        """
        Sets weights to the most recently added dataset;
        uses spline interpolation to weight data points

        Parameters:
        * `weights`: List of weights
        """
        last_data = self.get_last_data()
        last_data.set_weights(weights)
        self.set_last_data(last_data)

    def fit_model(self):
        """
        Fits the symbolic regression model
        """
        fit_data_list = self.get_fit_data_list()
        print()
        self.model.fit(fit_data_list)
        print()

    def plot_data(self, plot_path:str, x_field:str, y_field:str, x_scale:float, y_scale:float, 
                  x_units:str="", y_units:str="", x_limits:tuple=None, y_limits:tuple=None, 
                  conditions:dict={}, **settings) -> None:
        """
        Plots the data

        Parameters:
        * `plot_path`:  Path to save the plot
        * `x_field`:    Field to use for the x-axis
        * `y_field`:    Field to use for the y-axis
        * `x_scale`:    Factor to apply to x values
        * `y_scale`:    Factor to apply to y values
        * `x_units`:    Units for the x-axis
        * `y_units`:    Units for the y-axis
        * `x_limits`:   Limits to apply on the x-axis
        * `y_limits`:   Limits to apply on the y-axis
        * `conditions`: Conditions to constrain plotting
        """

        # Initialise
        if self.model == None:
            raise ValueError("The model has not been defined!")
        prep_plot(x_field, y_field, x_units, y_units)

        # Plot experimental data
        data_dict_list = self.get_data_dict_list(conditions)
        for data_dict in data_dict_list:
            x_list = [dd*x_scale for dd in data_dict[x_field]]
            y_list = [dd*y_scale for dd in data_dict[y_field]]
            plt.scatter(x_list, y_list, color=EXP_COLOUR, s=8**2)

        # Format and save
        set_limits(x_limits, y_limits)
        save_plot(plot_path, **settings)

    def plot_fit(self, plot_path:str, x_field:str, y_field:str, x_scale:float, y_scale:float, 
                 x_units:str="", y_units:str="", x_limits:tuple=None, y_limits:tuple=None, 
                 conditions:dict={}, **settings) -> None:
        """
        Plots the results

        Parameters:
        * `plot_path`:  Path to save the plot
        * `x_field`:    Field to use for the x-axis
        * `y_field`:    Field to use for the y-axis
        * `x_scale`:    Factor to apply to x values
        * `y_scale`:    Factor to apply to y values
        * `x_units`:    Units for the x-axis
        * `y_units`:    Units for the y-axis
        * `x_limits`:   Limits to apply on the x-axis
        * `y_limits`:   Limits to apply on the y-axis
        * `conditions`: Conditions to constrain plotting
        """

        # Initialise
        if self.model == None:
            raise ValueError("The model has not been defined!")
        prep_plot(x_field, y_field, x_units, y_units)

        # Plot experimental data
        data_dict_list = self.get_data_dict_list(conditions)
        if data_dict_list == []:
            return
        for data_dict in data_dict_list:
            x_list = [dd*x_scale for dd in data_dict[x_field]]
            y_list = [dd*y_scale for dd in data_dict[y_field]]
            plt.scatter(x_list, y_list, color=EXP_COLOUR, s=8**2)

        # Plot fitted data
        fit_data_list = self.get_fit_data_list(conditions)
        fit_dict_list = self.model.predict(fit_data_list)
        for fit_dict in fit_dict_list:
            x_list = [fd*x_scale for fd in fit_dict[x_field]]
            y_list = [fd*y_scale for fd in fit_dict[y_field]]
            plt.plot(x_list, y_list, color=CAL_COLOUR, linewidth=3)

        # Plot predicted data
        prd_data_list = self.get_prd_data_list(conditions)
        prd_dict_list = self.model.predict(prd_data_list)
        for prd_dict in prd_dict_list:
            x_list = [pd*x_scale for pd in prd_dict[x_field]]
            y_list = [pd*y_scale for pd in prd_dict[y_field]]
            plt.plot(x_list, y_list, color=VAL_COLOUR, linewidth=3)

        # Format and save
        set_limits(x_limits, y_limits)
        add_legend(
            calibration = len(fit_data_list) > 0,
            validation  = len(prd_data_list) > 0,
        )
        save_plot(plot_path, **settings)

    def export_fit(self, fields:list, file_path:str, conditions:dict={}) -> None:
        """
        Exports the predicted data
        
        Parameters:
        * `fields`:     List of fields to export
        * `file_path`:  The path to export the fitted data
        * `conditions`: Conditions to constrain export
        """

        # Initialise
        if self.model == None:
            raise ValueError("The model has not been defined!")
        
        # Get predictions
        data_list = self.get_data_list(conditions)
        if data_list == []:
            return
        prd_dict_list = self.model.predict(data_list)

        # Organise the predicted data into a single dictionary
        summary_dict = {}
        for i, (prd_dict, data) in enumerate(zip(prd_dict_list, data_list)):
            for field in fields:

                # Check that the field exists
                if not field in prd_dict.keys():
                    raise ValueError(f"One or more of the predicted outputs is missing the '{field}' field!")

                # Add to summary
                status = "cal" if data.is_fitting() else "val"
                new_field = f"{field}_{status}_{i+1}"
                summary_dict[new_field] = prd_dict[field]
        
        # Save the summarised dictionary
        dict_to_csv(summary_dict, file_path)

    def plot_1to1(self, plot_path:str, handle, label:str="", units:str="",
                  limits:tuple=None, conditions:dict={}) -> None:
        """
        Plots 1:1 comparison plots based on a function handle;
        the function must take a dictionary as an argument and
        return a list of values

        Parameters:
        * `plot_path`: Path to save the plot
        * `handle`:    The function handle
        * `label`:     Label to represent values
        * `units`:     Units to place beside label
        * `limits`:    Limits of the plot
        """

        # Check if model has been defined
        if self.model == None:
            raise ValueError("The model has not been defined!")
        
        # Get all data
        raw_fit_data_list = self.get_fit_data_list(conditions)
        raw_fit_dict_list = [data.get_data_dict() for data in raw_fit_data_list]
        sim_fit_dict_list = self.model.predict(raw_fit_data_list)
        raw_prd_data_list = self.get_prd_data_list(conditions)
        raw_prd_dict_list = [data.get_data_dict() for data in raw_prd_data_list]
        sim_prd_dict_list = self.model.predict(raw_prd_data_list)

        # Initialise values lists
        raw_fit_values_list = []
        raw_prd_values_list = []
        sim_fit_values_list = []
        sim_prd_values_list = []

        # Apply function handle to fitting data
        for rfd, sfd in zip(raw_fit_dict_list, sim_fit_dict_list):
            rfv, sfv = handle(rfd, sfd)
            raw_fit_values_list.append(rfv)
            sim_fit_values_list.append(sfv)

        # Apply function handle to predicted data
        for rpd, spd in zip(raw_prd_dict_list, sim_prd_dict_list):
            rpv, spv = handle(rpd, spd)
            raw_prd_values_list.append(rpv)
            sim_prd_values_list.append(spv)

        # Flatten values lists
        raw_fit_values_list = flatten(raw_fit_values_list)
        raw_prd_values_list = flatten(raw_prd_values_list)
        sim_fit_values_list = flatten(sim_fit_values_list)
        sim_prd_values_list = flatten(sim_prd_values_list)

        # Determine limits
        if limits == None:
            combined_list = raw_fit_values_list + raw_prd_values_list + sim_fit_values_list + sim_prd_values_list
            limits = (min(combined_list), max(combined_list))

        # Plot and save
        create_1to1(label, units, limits)
        plot_1to1(raw_fit_values_list, sim_fit_values_list, CAL_COLOUR)
        plot_1to1(raw_prd_values_list, sim_prd_values_list, VAL_COLOUR)
        save_plot(plot_path)

    def plot_equation(self, equation_path:str) -> None:
        """
        Saves an image of the equation
        """
        latex_equations = self.model.get_latex()
        if not isinstance(latex_equations, list):
            latex_equations = [latex_equations]
        save_latex(equation_path, latex_equations)

    def get_last_data(self) -> Dataset:
        """
        Returns the previously added dataset object
        """
        if len(self.data_list) == 0:
            raise ValueError("No datasets have been added!")
        return self.data_list[-1]

    def set_last_data(self, last_data) -> None:
        """
        Redefines the previously added dataset object

        Parameters:
        * `last_data`: The new last dataset object
        """
        if len(self.data_list) == 0:
            raise ValueError("No datasets have been added!")
        self.data_list[-1] = last_data

    def get_data_list(self, conditions:dict={}) -> list:
        """
        Gets the data list
        
        Parameters:
        * `conditions`: Conditions to constrain plotting

        Returns the list of datasets
        """
        new_data_list = []
        for data in self.data_list:
            has_data_list = [data.has_data(field, conditions[field]) for field in conditions.keys()]
            if not False in has_data_list:
                new_data_list.append(data)
        return new_data_list

    def get_data_dict_list(self, conditions:dict={}) -> list:
        """
        Gets the data dictionaries only
        
        Parameters:
        * `conditions`: Conditions to constrain plotting

        Returns the list of dictionaries of datasets
        """
        data_list = self.get_data_list(conditions)
        return [data.get_data_dict() for data in data_list]

    def get_fit_data_list(self, conditions:dict={}) -> list:
        """
        Returns the list of fitting datasets
        
        Parameters:
        * `conditions`: Conditions to constrain plotting

        Returns the list of dictionaries of datasets
        """
        data_list = self.get_data_list(conditions)
        data_list = [data for data in data_list if data.is_fitting()]
        data_list = deepcopy(data_list)
        return data_list

    def get_prd_data_list(self, conditions:dict={}) -> list:
        """
        Returns the list of prediction datasets
        
        Parameters:
        * `conditions`: Conditions to constrain plotting

        Returns the list of dictionaries of datasets
        """
        data_list = self.get_data_list(conditions)
        data_list = [data for data in data_list if not data.is_fitting()]
        data_list = deepcopy(data_list)
        return data_list

    def get_num_data(self) -> int:
        """
        Returns the number of datasets added
        """
        return len(self.data_list)

    def get_num_fit_data(self) -> int:
        """
        Returns the number of datasets added
        """
        return len([data for data in self.data_list if data.is_fitting()])
