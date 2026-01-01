"""
 Title:         Custom creep model that uses the derivative
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.io.dataset import data_to_array, sparsen_data, add_field, bind_data
from symbolic.regression.expression import replace_variables, julia_to_expression, expression_to_latex
from symbolic.regression.expression import evaluate_expression, round_expression
import numpy as np
from copy import deepcopy
from pysr import PySRRegressor, TemplateExpressionSpec
from symbolic.helper.derivative import differentiate_curve, integrate_curve

# Model class
class Model(__Model__):

    def initialise(self, **settings):
        """
        Initialises the model
        """

        # Define combine string
        # x0 = time
        # x1 = stress
        # x2 = temperature
        # y0 = strain rate
        # y1 = time-to-failure (ttf)
        self.combine = """
            z0 = f0(x0,x1,x2);
            z1 = f1(x1,x2);
            e0 = abs((y0-z0)/y0);
            e1 = abs((y1-z1)/y1);
            ef = (e0 + e1)/2;
            ef
        """

        # Define regressor for strain/ttf predictions
        spec = TemplateExpressionSpec(
            expressions    = ["f0", "f1"],
            variable_names = ["x0", "x1", "x2", "y0", "y1"],
            combine        = self.combine
        )
        self.reg = PySRRegressor(
            expression_spec  = spec,
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 128,
            precision        = 64,
            verbosity        = 1,
            binary_operators = ["+", "*", "/"],
            unary_operators  = ["log", "exp"],
            # complexity_of_variables = 2,
            # binary_operators = ["+", "*", "^", "/"],
            # constraints      = {"^": (-1, 1)},
            # unary_operators  = ["log", "exp"],
            elementwise_loss = "take_first(p, t, w) = p",
            output_directory = self.output_path,
        )

        # Define fields and initialise auxiliaries
        self.julia = None
        self.add_ttf = lambda dd : dd.update({"ttf": [max(dd["time"])]*len(dd["time"])}) or dd # returns dd

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Differentiate strain for strain rate
        data_list = deepcopy(data_list)
        for data in data_list:
            data_dict = data.get_data_dict()
            data_dict = differentiate_curve(data_dict, "time", "strain")
            data.set_data_dict(data_dict)
        
        # Process data
        data_list = bind_data(data_list, "time", (1.0, np.inf))
        data_list = add_field(data_list, self.add_ttf)
        data_list = sparsen_data(data_list, 64)

        # Fit the regression model
        input_data = data_to_array(data_list, ["time", "stress", "temperature", "strain", "ttf"])
        output_data = np.zeros(len(input_data))
        weights = self.get_fit_weights(data_list)
        self.reg.fit(input_data, output_data, weights=weights)

        # Save the julia expression
        self.julia = self.reg.get_best()["julia_expression"]
        self.expression = julia_to_expression(self.julia, self.combine)

    def predict(self, data_list:list) -> list:
        """
        Predicts data using fit

        Parameters:
        * `data_list`: List of dictionaries containing data

        Returns the list of predicted data
        """
        
        # Iterate through data
        prd_dict_list = []
        for data in data_list:

            # Get data
            stress = data.get_data("stress")
            temperature = data.get_data("temperature")
            
            # Predict time-to-failure
            input_dict = {"x1": [stress], "x2": [temperature]}
            ttf = evaluate_expression(self.expression, "z1", input_dict)[0]
            
            # Predict creep strain curve
            num_data = 100
            time_list = np.linspace(0.1, ttf, num_data).tolist()
            input_dict = {"x0": time_list, "x1": num_data*[stress], "x2": num_data*[temperature]}
            strain_list = evaluate_expression(self.expression, "z0", input_dict, 0.0)

            # Combine and append
            prd_dict = {"time": [0]+time_list, "strain": [0]+strain_list}
            prd_dict_list.append(prd_dict)
        
        # Integrate and return predictions
        prd_dict_list = [integrate_curve(prd_dict, "time", "strain") for prd_dict in prd_dict_list]
        return prd_dict_list

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        
        # Check that the model has been fitted
        if self.julia == None:
            raise ValueError("The model has not been fitted!")
    
        # Convert the expressions into LaTeX
        rounded_expression = round_expression(self.expression, 5)
        latex_dict = expression_to_latex(rounded_expression)
        variable_map = {
            "x0": r't',
            "x1": r'\sigma',
            "x2": r'T',
            "z0": r'\dot{\varepsilon}',
            "z1": r't_{f}',
        }
        latex_dict = replace_variables(latex_dict, variable_map)
        
        # Identify expressions and return
        latex_expressions = [latex_dict[p] for p in ["z0", "z1"]]
        return latex_expressions

    def set_julia(self, julia:str) -> None:
        """
        Sets the julia expression without fitting

        * `julia`: The julia expression
        """
        self.julia = julia
        self.expression = julia_to_expression(self.julia, self.combine)
