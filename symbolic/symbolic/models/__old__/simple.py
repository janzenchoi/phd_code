"""
 Title:         Simple creep model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.io.dataset import data_to_array, sparsen_data, posify_data, add_field
from symbolic.regression.expression import replace_variables, julia_to_expression, expression_to_latex
from symbolic.regression.expression import evaluate_expression, round_expression
import numpy as np
from pysr import PySRRegressor, TemplateExpressionSpec

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
        # y0 = strain
        # y1 = time-to-failure (ttf)
        self.kr_combine = """
            A = 10^fA(x1,x2); n = 0.3333; B = 10^fB(x1,x2); k = abs(fk(x1,x2));
            z0 = A*x0^n + B*exp(k*x0) + f0(x0,x1,x2);
            z1 = f1(x1,x2);
            ((y0-z0)/y0)^2 + ((y1-z1)/y1)^2
        """

        # Define regressor for strain/ttf predictions
        kr_spec = TemplateExpressionSpec(
            expressions    = ["f0", "f1", "fA", "fB", "fk"],
            variable_names = ["x0", "x1", "x2", "y0", "y1"],
            # parameters     = {"p": 5},
            combine        = self.kr_combine
        )
        self.kr_reg = PySRRegressor(
            expression_spec  = kr_spec,
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 64,
            precision        = 64,
            # complexity_of_variables = 2,
            binary_operators = ["+", "*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            unary_operators  = ["log", "exp"],
            elementwise_loss = "take_first(p, t, w) = p",
            output_directory = self.output_path,
        )

        # Define fields and initialise auxiliaries
        self.kr_julia = None
        self.add_ttf = lambda dd : dd.update({"ttf": [max(dd["time"])]*len(dd["time"])}) or dd # returns dd

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process data
        data_list = posify_data(data_list)
        data_list = sparsen_data(data_list, 100)
        data_list = add_field(data_list, self.add_ttf)

        # Fit the regression model
        input_data = data_to_array(data_list, ["time", "stress", "temperature", "strain", "ttf"])
        output_data = np.zeros(len(input_data))
        weights = self.get_fit_weights(data_list)
        self.kr_reg.fit(input_data, output_data, weights=weights)

        # Save the julia expression
        self.kr_julia = self.kr_reg.get_best()["julia_expression"]
        self.kr_expression = julia_to_expression(self.kr_julia, self.kr_combine)

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
            ttf = evaluate_expression(self.kr_expression, "z1", input_dict)[0]
            
            # Predict creep strain curve
            num_data = 100
            time_list = np.linspace(0.1, ttf, num_data).tolist()
            input_dict = {"x0": time_list, "x1": num_data*[stress], "x2": num_data*[temperature]}
            strain_list = evaluate_expression(self.kr_expression, "z0", input_dict)

            # Combine and append
            prd_dict = {"time": [0]+time_list, "strain": [0]+strain_list}
            prd_dict_list.append(prd_dict)
        
        # Return predictions
        return prd_dict_list

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        
        # Check that the model has been fitted
        if self.kr_julia == None:
            raise ValueError("The model has not been fitted!")
    
        # Convert the expressions into LaTeX
        rounded_expression = round_expression(self.kr_expression, 5)
        latex_dict = expression_to_latex(rounded_expression)
        variable_map = {
            "x0": r't',
            "x1": r'\sigma',
            "x2": r'T',
            "z0": r'\varepsilon',
            "z1": r't_{f}'
        }
        latex_dict = replace_variables(latex_dict, variable_map)
        
        # Identify expressions and return
        latex_expressions = [latex_dict[p] for p in ["z0", "z1", "A", "n", "B", "k"]]
        return latex_expressions
