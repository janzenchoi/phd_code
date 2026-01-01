"""
 Title:         Basic tensile model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.regression.expression import replace_variables, equate_to
from symbolic.io.dataset import data_to_array, sparsen_data
from pysr import PySRRegressor

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """
        self.regressor = PySRRegressor(
            populations          = 32,
            population_size      = 32,
            maxsize              = 32,
            niterations          = 500,
            binary_operators     = ["+", "*", "^"],
            unary_operators      = ["cos", "sin", "exp", "log", "inv(x) = 1/x"],
            extra_sympy_mappings = {"inv": lambda x: 1/x},
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
        self.regressor.fit(input_data, output_data, weights=weights)

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
            output_data = self.regressor.predict(input_data)
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
        latex_string = self.regressor.latex()
        latex_string = replace_variables(latex_string, [r'\epsilon', r'\dot{\varepsilon}', r'T'])
        latex_string = equate_to(r'\sigma', latex_string)
        return [latex_string]
