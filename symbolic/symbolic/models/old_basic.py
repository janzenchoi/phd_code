"""
 Title:         Basic model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from pysr import PySRRegressor
from symbolic.models.__model__ import __Model__
from symbolic.regression.expression import replace_variables, equate_to
from symbolic.io.dataset import data_to_array, sparsen_data, posify_data

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
            niterations      = 256,
            complexity_of_variables = 2,
            binary_operators = ["+", "*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            unary_operators  = ["exp", "log"],
            elementwise_loss = "loss(p, t, w) = w*(p-t)^2",
            output_directory = self.output_path,
        )
        self.input_fields = ["time", "stress", "temperature"]

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 256)
        input_data = data_to_array(data_list, self.input_fields)
        output_data = data_to_array(data_list, ["strain"])
        weights = self.get_fit_weights(data_list)
        self.regressor.fit(input_data, output_data, weights=weights)

    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the list of predicted data
        """
        # Sparsen data
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 256)
        
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

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        strain_reg_ls = self.regressor.latex()
        variable_map = {"x0": r't', "x1": r'\sigma', "x2": r'T'}
        strain_reg_ls = replace_variables(strain_reg_ls, variable_map)
        strain_reg_ls = equate_to(r'\epsilon', strain_reg_ls)
        return [strain_reg_ls]
