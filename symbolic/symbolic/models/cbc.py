"""
 Title:         Characteristic-based Creep
 Description:   Performs the symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from pysr import PySRRegressor
from symbolic.models.__model__ import __Model__
from symbolic.helper.general import round_sf
from symbolic.regression.expression import replace_variables, equate_to
from symbolic.io.dataset import data_to_array
from symbolic.io.files import dict_to_csv

# Model class
class Model(__Model__):

    def initialise(self, target:str):
        """
        Initialises the model

        Parameters:
        * `target`: Field to predict
        """
        self.target = target
        self.regressor = PySRRegressor(
            populations      = 32,
            population_size  = 32,
            maxsize          = 32,
            niterations      = 256,
            complexity_of_variables = 5,
            binary_operators = ["+", "*", "^", "/"],
            constraints      = {"^": (-1, 1)},
            # unary_operators  = ["log", "exp"],
            unary_operators  = ["log"],
            elementwise_loss = "loss(p, t, w) = w*(p-t)^2",
            output_directory = self.output_path,
        )

    def fit(self, data_list:list) -> None:
        """
        Performs the fitting

        Parameters:
        * `data_list`: List of dictionaries containing data
        """
        input_data = data_to_array(data_list, ["stress", "temperature"])
        output_data = data_to_array(data_list, [self.target])
        weights = self.get_fit_weights(data_list)
        self.regressor.fit(input_data, output_data, weights=weights)

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

            # Predict time-to-failure
            input_data = data_to_array([data], ["stress", "temperature"])
            output_data = self.regressor.predict(input_data)

            # Combine and append
            stress = data.get_data("stress")
            temperature = data.get_data("temperature")
            prd_dict = {"stress": stress, "temperature": temperature, self.target: output_data.tolist()}
            prd_dict_list.append(prd_dict)
        
        # Return predictions
        return prd_dict_list

    def save_equation(self) -> str:
        """
        Gets the best equation
        """
        best_equation = self.regressor.get_best()["equation"]
        with open(f"{self.output_path}/equation.txt", "w") as fh:
            fh.write(best_equation)
        return best_equation
    
    def export_errors(self, data_list:list) -> None:
        """
        Exports errors of the fit

        Parameters:
        * `data_list`: List of dictionaries containing data
        """
        
        # Iterate through data
        are_list = []
        for data in data_list:

            # Predict time-to-failure
            input_data = data_to_array([data], ["stress", "temperature"])
            output_data = self.regressor.predict(input_data)

            # Prepare outputs
            fit_output_list = data.get_data_dict()[self.target]
            prd_output_list = output_data.tolist()

            # Calculate error and append
            are = np.average([abs(f-p) for f, p in zip(fit_output_list, prd_output_list)])
            are = round_sf(are*100, 5)/np.average(fit_output_list)
            are_list.append(are)
            print(are)

        # Save errors
        dict_to_csv({"are": are_list}, f"{self.output_path}/are.txt")

    def get_latex(self) -> str:
        """
        Returns the LaTeX equation of the final fit; must be overridden
        """
        strain_reg_ls = self.regressor.latex()
        variable_map = {"x0": r'\sigma', "x1": r'T'}
        strain_reg_ls = replace_variables(strain_reg_ls, variable_map)
        equate_map = {"mcr": "epsdot_m", "ttf": "t_f", "stf": "eps_f", "rttf": "t_f"}
        strain_reg_ls = equate_to(equate_map[self.target], strain_reg_ls)
        return [strain_reg_ls]
