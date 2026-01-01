"""
 Title:         Custom creep model
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
from symbolic.models.__model__ import __Model__
from symbolic.helper.general import round_sf
from symbolic.io.dataset import data_to_array, sparsen_data, bind_data
from symbolic.io.files import dict_to_csv
from symbolic.regression.expression import replace_variables, julia_to_expression, expression_to_latex
from symbolic.regression.expression import evaluate_expression, round_expression, set_parameters
import numpy as np
from copy import deepcopy
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
        self.combine = """
            A = 10^(p[1]); m = abs(p[2]); n = abs(p[3]); q = 10^(p[4]);
            z0 = A * x0^m * x1^n * exp(-q/8.3145/x2) + f0(x0,x1,x2);
            re0 = abs((y0-z0)/y0);
            ref = re0;
            ref
        """

        "10^(-0.97051) * x0^0.80916 * x1^4.6085 * exp(-5.3243/8.3145/x2)"
        "10^(-0.60897) * x0^0.81596 * x1^4.8925 * exp(-5.3528/8.3145/x2)"

        # Set parameters
        # parameter_values = [-0.97051, 0.80916, 4.6085, 5.3243] # st
        # parameter_values = [-0.60897, 0.81596, 4.8925, 5.3528] # all
        # parameter_map = dict(zip([f"p[{i+1}]" for i in range(len(parameter_values))], parameter_values))
        # self.combine = set_parameters(self.combine, parameter_map)

        # Define regressor for strain predictions
        spec = TemplateExpressionSpec(
            expressions    = ["f0"],
            variable_names = ["x0", "x1", "x2", "y0"],
            parameters     = {"p": 4},
            combine        = self.combine
        )
        self.reg = PySRRegressor(
            expression_spec  = spec,
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 1024,
            complexity_of_variables = 2,
            binary_operators = ["+", "*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            unary_operators  = ["exp", "log"],
            elementwise_loss = "take_first(p, t, w) = w*p",
            output_directory = self.output_path,
            precision        = 64,
            verbosity        = 1,
        )

        # Define fields and initialise auxiliaries
        self.julia = None

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process the data
        data_list = self.process_data_list(data_list)

        # Fit the regression model
        input_data = data_to_array(data_list, ["time", "stress", "temperature", "strain"])
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
            ttf = max(data.get_data("time"))
            
            # Predict creep strain curve
            num_data = 100
            time_list = np.linspace(0.1, ttf, num_data).tolist()
            input_dict = {"x0": time_list, "x1": num_data*[stress], "x2": num_data*[temperature]}
            strain_list = evaluate_expression(self.expression, "z0", input_dict, 0.0)

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
        if self.julia == None:
            raise ValueError("The model has not been fitted!")
    
        # Convert the expressions into LaTeX
        rounded_expression = round_expression(self.expression, 5)
        latex_dict = expression_to_latex(rounded_expression)
        variable_map = {
            "x0": r't',
            "x1": r'\sigma',
            "x2": r'T',
            "z0": r'\varepsilon',
        }
        latex_dict = replace_variables(latex_dict, variable_map)
        
        # Identify expressions and return
        latex_expressions = [latex_dict[p] for p in ["z0", "A", "m", "n", "q"]]
        return latex_expressions

    def process_data_list(self, data_list:list, time_upper:float=np.inf) -> None:
        """
        Processes the data list

        Parameters:
        * `data_list`:  List of dictionaries containing data
        * `time_upper`: Upper bound of time

        Returns the processed data list
        """
        data_list = deepcopy(data_list)
        data_list = bind_data(data_list, "time", (1.0, time_upper))
        data_list = sparsen_data(data_list, 32)
        return data_list

    def set_julia(self, julia:str) -> None:
        """
        Sets the julia expression without fitting

        * `julia`: The julia expression
        """
        self.julia = julia
        self.expression = julia_to_expression(self.julia, self.combine)

    def export_errors(self, data_list:list) -> None:
        """
        Exports the errors

        Parameters:
        * `data_list`: List of dictionaries containing data
        """

        # Process the data
        for i, data in enumerate(data_list):
            max_time = max(data.get_data("time"))
            data_list[i] = self.process_data_list([data_list[i]], time_upper=max_time)[0]

        # Define the errors
        error_names = ["re0", "ref"]
        error_dict = {"dataset": ["fitting", "predicting"]}
        for error_key in error_names:
            error_dict[error_key] = [[], []]

        # Calculate the errors
        for data in data_list:

            # Get data
            data_dict = data.get_data_dict()

            # Define input
            input_dict = {
                "x0": data_dict["time"],
                "x1": [data_dict["stress"]]*len(data_dict["time"]),
                "x2": [data_dict["temperature"]]*len(data_dict["time"]),
                "y0": data_dict["strain"],
            }

            # Evaluate for errors
            for error_key in error_names:
                error_list = evaluate_expression(self.expression, error_key, input_dict, True)
                if data.is_fitting():
                    error_dict[error_key][0] += error_list
                else:
                    error_dict[error_key][1] += error_list

        # Average the errors
        for error_key in error_names:
            error_dict[error_key][0] = f"{round_sf(np.average(error_dict[error_key][0]), 5)*100}%" # %
            error_dict[error_key][1] = f"{round_sf(np.average(error_dict[error_key][1]), 5)*100}%" # %

        # Save the errors
        error_path = f"{self.output_path}/error.csv"
        dict_to_csv(error_dict, error_path)
