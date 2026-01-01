"""
 Title:         Basic creep model with submodels
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.io.dataset import data_to_array, sparsen_data, posify_data, add_field
from symbolic.regression.expression import replace_variables, equate_to, submodel_to_latex
from symbolic.regression.submodel import create_tes
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
        # x1 = stress
        # x2 = temperature
        # x3 = strain
        # self.ttf_submodels = [
        #     "exp(P/x2-C)", # Larson-Miller
        # ]
        self.ttf_reg = PySRRegressor(
            populations      = 32,
            population_size  = 32,
            maxsize          = 16,
            niterations      = 64,
            binary_operators = ["+", "*", "/"],
            elementwise_loss = "loss(p, t) = abs(p - t)",
            output_directory = self.output_path,
        )

        # Define regressor for strain
        # x0 = time
        # x1 = stress
        # x2 = temperature
        self.strain_ni = 3 # number of inputs
        self.strain_submodels = [
            # "x0^n",
            # "x1^m",
            # "exp(k*x0)",
            # "exp(-k/x2)",
            # "log(k*x0+1)"
            # "x0^f0(x1,x2)",
            # "x1^f1(x2)",
            # "exp(k*x0)",
            # "exp(-k/x2)",
            # "log(x0*f2(x1,x2)+1)"
        ]
        strain_tes = create_tes(self.strain_ni, self.strain_submodels)
        self.strain_reg = PySRRegressor(
            expression_spec  = strain_tes,
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 256,
            complexity_of_variables = 3,
            binary_operators = ["+", "*", "/"],
            elementwise_loss = "loss(p, t, w) = w*abs(p-t)",
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
        ttf_expression = self.ttf_reg.latex()
        ttf_expression = replace_variables(ttf_expression, [r'\sigma', r'T'])
        ttf_expression = equate_to(r't_f', ttf_expression)

        # Get strain latex equation
        strain_julia = self.strain_reg.get_best()["julia_expression"]
        strain_expression = submodel_to_latex(strain_julia, self.strain_ni, self.strain_submodels)
        strain_expression = replace_variables(strain_expression, [r't', r'\sigma', r'T'])
        strain_expression = equate_to(r'\varepsilon', strain_expression)

        # Combine and return
        return [ttf_expression, strain_expression]
