"""
 Title:         Evaluates creep expressions
 Description:   Quickly evaluates expressions
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.helper.general import round_sf
from symbolic.io.dataset import posify_data, sparsen_data
from symbolic.io.files import dict_to_csv
from symbolic.regression.expression import process_str, replace_variables, expression_to_latex
from symbolic.regression.expression import evaluate_expression, round_expression
import numpy as np
from copy import deepcopy

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """
        self.julia = None
        self.expression = None

    def process_data(self, data_list:list) -> list:
        """
        Processes the data list

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the processed data list
        """
        data_list = deepcopy(data_list)
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 128)
        return data_list
    
    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the list of predicted data
        """

        # Process data
        data_list = self.process_data(data_list)
        
        # Iterate through data
        prd_dict_list = []
        for data in data_list:

            # Get data
            stress = data.get_data("stress")
            temperature = data.get_data("temperature")
            time_list = data.get_data("time")
            
            # max_time = max(time_list)
            # time_list = [t/max_time for t in time_list]

            # Evaluate creep strain curve
            input_dict = {"x0": time_list, "x1": len(time_list)*[stress], "x2": len(time_list)*[temperature]}
            strain_list = evaluate_expression(self.expression, "f", input_dict, 0.0)

            # time_list = [t*max_time for t in time_list]

            # Combine and append
            prd_dict = {"time": [0]+time_list, "strain": [0]+strain_list}
            prd_dict_list.append(prd_dict)
        
        # Return predictions
        return prd_dict_list

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
    
        # Convert the expressions into LaTeX
        rounded_expression = round_expression(self.expression, 5)
        latex_dict = expression_to_latex(rounded_expression)
        variable_map = {
            "x0": r't',
            "x1": r'\sigma',
            "x2": r'T'
        }
        latex_dict = replace_variables(latex_dict, variable_map)
        
        # Identify expressions and return
        latex_expressions = [latex_dict[p] for p in ["f"]]
        return latex_expressions

    def set_julia(self, julia:str) -> None:
        """
        Sets the julia expression
        
        Parameters:
        * `julia`: The julia expression to be set
        """
        # self.expression = julia_to_expression("f", julia)
        julia = process_str(julia)
        self.julia = f"f = {julia}"
        self.expression = {"f": julia}

    def export_errors(self, data_list:list) -> None:
        """
        Exports errors of the fit

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process data
        data_list = self.process_data(data_list)

        # Iterate through data
        cal_nrmse_list = []
        val_nrmse_list = []
        for data in data_list:

            # Get data
            stress = data.get_data("stress")
            temperature = data.get_data("temperature")
            time_list = data.get_data("time")

            # Predict creep strain curve
            input_dict = {"x0": time_list, "x1": len(time_list)*[stress], "x2": len(time_list)*[temperature]}
            prd_output_list = evaluate_expression(self.expression, "f", input_dict, 0.0)

            # Calculate error and append
            fit_output_list = data.get_data_dict()["strain"]
            mse = np.average([(f-p)**2 for f, p in zip(fit_output_list, prd_output_list)])
            nrmse = np.sqrt(mse)/np.average(fit_output_list)
            nrmse = round_sf(nrmse*100, 5)

            # Sort calibration/valdation errors
            if data.is_fitting():
                cal_nrmse_list.append(nrmse)
            else:
                val_nrmse_list.append(nrmse)

        # Save errors
        error_dict = {
            "cal_nrmse":  round_sf(cal_nrmse_list, 5),
            "val_nrmse":  round_sf(val_nrmse_list, 5),
            "cal_anrmse": round_sf(np.average(cal_nrmse_list), 5),
            "val_anrmse": round_sf(np.average(val_nrmse_list), 5),
        }
        dict_to_csv(error_dict, f"{self.output_path}/error.csv")
