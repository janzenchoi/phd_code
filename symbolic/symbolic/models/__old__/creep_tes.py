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
            maxsize          = 32,
            niterations      = 64,
            binary_operators = ["*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            elementwise_loss = "loss(prediction, target) = (prediction - target)^2",
            output_directory = self.output_path,
        )

        # Define regressor for strain
        # x0 = time
        # x1 = stress
        # x2 = temperature
        # x3 = time3 (t^(1/3))
        self.strain_ni = 4 # number of inputs
        self.strain_submodels = [
            "A * x3",             # Andrade (Primary)
            "A * x0^n * x1^m",    # Norton-Bailey (Primary)
            "A*log(x0)",          # Logarithmic (Primary) 
            "A*x0",               # Linear (Secondary)
            "t1*(1-exp(-t2*x0))",  # Theta-projection (Primary)
            "t3*(exp(t4*x0)-1)", # Theta-projection (Tertiary)
            "(q1*q2*x0)^(1/q2)",  # Phi (Primary, Tertiary)
            "log(s1*s2*x0+1)/s2", # Omega 
            
            # "A * exp(n*log(x2))",   # Power law
            # "A * exp(-B/8.314/x3)", # Arrhenius
        ]
        strain_tes = create_tes(self.strain_ni, self.strain_submodels)
        self.strain_reg = PySRRegressor(
            expression_spec = strain_tes,
            populations     = 32,
            population_size = 32,
            maxsize         = 32,
            niterations     = 256,
            # complexity_of_variables = 3,
            binary_operators= ["+", "*", "/"],
            elementwise_loss= "loss(prediction, target, weight) = weight*(prediction - target)^2",
            output_directory= self.output_path,
        )

        # Define fields and initialise auxiliaries
        self.add_time3 = lambda dd : dd.update({"time3": [t**(1/3) for t in dd["time"]]}) or dd # returns dd

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process data
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 100)
        data_list = add_field(data_list, self.add_time3)

        # Fit the time-to-failure regression model
        input_data = data_to_array(data_list, ["stress", "temperature"])
        ttf_list = [max(data.get_data("time")) for data in data_list]
        output_data = np.array([np.array([ttf]) for ttf in ttf_list])
        self.ttf_reg.fit(input_data, output_data)

        # Fit the strain regression model
        input_data = data_to_array(data_list, ["time", "stress", "temperature", "time3"])
        output_data = data_to_array(data_list, ["strain"])
        weights = self.get_fit_weights(data_list)
        self.strain_reg.fit(input_data, output_data, weights=weights)

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
        data_list = add_field(data_list, self.add_time3)
        
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
            input_ttf_data = data_to_array([ttf_data], ["time", "stress", "temperature", "time3"])
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
        strain_expression = replace_variables(strain_expression, [r't', r'\sigma', r'T', r't^{1/3}'])
        strain_expression = equate_to(r'\varepsilon', strain_expression)

        # Combine and return
        return [ttf_expression, strain_expression]
