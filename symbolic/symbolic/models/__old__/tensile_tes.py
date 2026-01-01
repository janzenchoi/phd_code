"""
 Title:         Basic tensile model with submodels
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.io.dataset import data_to_array, sparsen_data
from symbolic.regression.expression import replace_variables, equate_to, submodel_to_latex
from symbolic.regression.submodel import create_tes
from pysr import PySRRegressor

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """

        # Define expressions for yield predictions
        # x0 = strain
        # x1 = strain_rate
        # x2 = temperature
        self.yield_submodels = [
            "A * x0 ^ n"                    # Swift
            "K + Q * (1 - exp(-B * x0))", # Voce
        ]

        # Define expressions for stress predictions
        # x0 = strain
        # x1 = strain_rate
        # x2 = temperature
        self.stress_submodels = [
            "x0 ^ f0(x2)",
            "exp(-x0*f3(x2))",
            # "exp(-A/8.314/x2)"
            # "A * x0 ^ n",           # Hollomon (Power-Law)
            # "A + B * x0 ^ n",       # Ludwik
            # "A - B * exp(-C * x0)", # Voce
            # "A * exp(-B * x0)",     # Voce
        ]
        stress_spec = create_tes(3, self.stress_submodels)

        # Define regressor for stress predictions
        self.stress_regressor = PySRRegressor(
            expression_spec      = stress_spec,
            populations          = 64,
            population_size      = 64,
            maxsize              = 32,
            niterations          = 500,
            binary_operators     = ["+", "*", "/", "-"],
            elementwise_loss     = "loss(prediction, target, weight) = weight*(prediction - target)^2",
            output_directory     = self.output_path,
        )

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """
        data_list = [sparsen_data(data, 100) for data in data_list]
        input_data = data_to_array(data_list, ["strain", "strain_rate", "temperature"])
        output_data = data_to_array(data_list, ["stress"])
        weights = self.get_fit_weights(data_list)
        self.stress_regressor.fit(input_data, output_data, weights=weights)

    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the list of predicted data
        """
        data_list = [sparsen_data(data, 100) for data in data_list]
        prd_dict_list = []
        for data in data_list:
            input_data = data_to_array([data], ["strain", "strain_rate", "temperature"])
            output_data = self.stress_regressor.predict(input_data)
            prd_dict = {
                "strain": [0] + [d[0] for d in input_data.tolist()],
                "stress": [0] + output_data.tolist()
            }
            prd_dict_list.append(prd_dict)
        return prd_dict_list

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        
        # Get expression for stress predictions
        stress_julia = self.stress_regressor.get_best()["julia_expression"]
        stress_expression = submodel_to_latex(stress_julia, 3, self.stress_submodels)
        stress_expression = replace_variables(stress_expression, [r'\epsilon', r'\dot{\varepsilon}', r'T'])
        stress_expression = equate_to(r'\sigma', stress_expression)
        
        # Combine expressions and return
        expressions = [stress_expression]
        return expressions
