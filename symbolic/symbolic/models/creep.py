"""
 Title:         Basic model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from pysr import PySRRegressor
from symbolic.helper.general import round_sf
from symbolic.io.files import dict_to_csv
from symbolic.models.__model__ import __Model__
from symbolic.regression.expression import replace_variables, equate_to
from symbolic.io.dataset import data_to_array, sparsen_data, posify_data
from copy import deepcopy

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """
        self.regressor = PySRRegressor(
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 1024,
            complexity_of_variables = 2,
            binary_operators = ["+", "*", "^", "/"],
            # constraints      = {"^": (-1, 1)},
            unary_operators  = ["exp", "log"],
            elementwise_loss = "loss(p, t, w) = w*(p-t)^2",
            # elementwise_loss = "loss(p, t, w) = w*((p-t)/t)^2",
            output_directory = self.output_path,
        )
        self.input_fields = ["time", "stress", "temperature"]

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

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """
        
        # Perform fit
        data_list = self.process_data(data_list)
        input_data = data_to_array(data_list, self.input_fields)
        output_data = data_to_array(data_list, ["strain"])
        weights = self.get_fit_weights(data_list)
        self.regressor.fit(input_data, output_data, weights=weights)
    
    def save_equation(self) -> str:
        """
        Gets the best equation
        """
        best_equation = self.regressor.get_best()["equation"]
        with open(f"{self.output_path}/equation.txt", "w") as fh:
            fh.write(best_equation)
        return best_equation

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

            # Predict strain
            input_data = data_to_array([data], self.input_fields)
            output_data = self.regressor.predict(input_data)

            # Combine and append
            prd_dict = {
                "time":   [0] + [d[0] for d in input_data.tolist()],
                "strain": [0] + output_data.tolist()
            }
            prd_dict_list.append(prd_dict)
        
        # Return predictions
        return prd_dict_list

    def export_errors(self, data_list:list) -> None:
        """
        Exports the errors

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process data
        data_list = self.process_data(data_list)
        
        # Iterate through data
        cal_nrmse_list = []
        val_nrmse_list = []
        for data in data_list:

            # Predict strain
            input_data = data_to_array([data], self.input_fields)
            output_data = self.regressor.predict(input_data)

            # Prepare output
            fit_output_list = data.get_data_dict()["strain"]
            prd_output_list = output_data.tolist()

            # Calculate error and append
            mse = np.average([(f-p)**2 for f, p in zip(fit_output_list, prd_output_list)])
            nrmse = np.sqrt(mse)/np.average(fit_output_list)*100

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

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        strain_reg_ls = self.regressor.latex()
        variable_map = {"x0": r't', "x1": r'\sigma', "x2": r'T'}
        strain_reg_ls = replace_variables(strain_reg_ls, variable_map)
        strain_reg_ls = equate_to(r'\epsilon', strain_reg_ls)
        return [strain_reg_ls]
