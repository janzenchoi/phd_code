"""
 Title:         Basic creep model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.regression.expression import replace_variables, equate_to
from symbolic.io.dataset import data_to_array, sparsen_data, posify_data
import numpy as np
from pysr import PySRRegressor
from copy import deepcopy

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """

        # Define regressor for time-to-failure
        self.ttf_reg = PySRRegressor(
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 64,
            binary_operators = ["*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            elementwise_loss = "loss(prediction, target) = (prediction - target)^2",
            output_directory = self.output_path,
        )

        # Define regressor for strain
        self.strain_reg = PySRRegressor(
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 256,
            binary_operators = ["+", "*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            unary_operators  = ["log", "exp"],
            elementwise_loss = "loss(prediction, target, weight) = weight*(prediction - target)^2",
            output_directory = self.output_path,
        )

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process data
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 100)

        # Fit the strain regression model
        input_data = data_to_array(data_list, ["time", "stress", "temperature"])
        output_data = data_to_array(data_list, ["strain"])
        weights = self.get_fit_weights(data_list)
        self.strain_reg.fit(input_data, output_data, weights=weights)

        # Fit the time-to-failure regression model
        input_data = data_to_array(data_list, ["stress", "temperature"])
        ttf_list = [max(data.get_data("time")) for data in data_list]
        output_data = np.array([np.array([ttf]) for ttf in ttf_list])
        self.ttf_reg.fit(input_data, output_data)

    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the list of predicted data
        """

        # Sparsen data
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 100)
        
        # Iterate through data
        prd_dict_list = []
        for data in data_list:

            # Predict time-to-failure
            input_data = data_to_array([data], ["stress", "temperature"])
            time_failure = self.ttf_reg.predict(input_data)[0]
            
            # Predict creep strain curve
            time_list = np.linspace(0.1, time_failure, len(data.get_data("time"))).tolist()
            ttf_data = deepcopy(data)
            ttf_data.set_data("time", time_list)
            input_ttf_data = data_to_array([ttf_data], ["time", "stress", "temperature"])
            output_ttf_data = self.strain_reg.predict(input_ttf_data)

            # Combine and append
            prd_dict = {
                "time":   [0] + [d[0] for d in input_ttf_data.tolist()],
                "strain": [0] + output_ttf_data.tolist()
            }
            prd_dict_list.append(prd_dict)
        
        # Return predictions
        return prd_dict_list

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """

        # Get time-to-failure latex equation
        ttf_reg_ls = self.ttf_reg.latex()
        variable_map = {"x0": r'\sigma', "x1": r'T'}
        ttf_reg_ls = replace_variables(ttf_reg_ls, variable_map)
        ttf_reg_ls = equate_to(r't_f', ttf_reg_ls)

        # Get strain latex equation
        strain_reg_ls = self.strain_reg.latex()
        variable_map = {"x0": r't', "x1": r'\sigma', "x2": r'T'}
        strain_reg_ls = replace_variables(strain_reg_ls, variable_map)
        strain_reg_ls = equate_to(r'\epsilon', strain_reg_ls)
        
        # Combine and return
        return [ttf_reg_ls, strain_reg_ls]
