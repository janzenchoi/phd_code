"""
 Title:         Optimise
 Description:   Functions for quick optimisation
 Author:        Janzen Choi

"""

# Libraries
import inspect
import numpy as np
import matplotlib.pyplot as plt
import osfem.models_ as models_
from osfem.general import round_sf
from osfem.plotter import create_1to1, plot_1to1, lobf_1to1, save_plot, CAL_COLOUR, VAL_COLOUR

# PYMOO libraries
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

# Define available fields
FIELD_INFO_DICT = {
    "ttf": {"scale": 1/3600, "units": "h",     "label": r"$t_{f}$"},
    "stf": {"scale": 1,      "units": "mm/mm", "label": r"$\epsilon_{f}$"},
    "mcr": {"scale": 1,      "units": "1/h",   "label": r"$\dot{\epsilon}_{min}$"},
}

# Model class
class Model:

    def __init__(self, model_name:str):
        """
        Initialises the model
        """
        self.model_name = model_name
        self.model = get_model(model_name)
        self.field = model_name.split("_")[0]
        self.opt_params = None

    def optimise(self, data_list:list, l_bound:tuple, u_bound:tuple):
        """
        Runs optimisation

        Parameters:
        * `data_list`: List of data dictionaries
        * `l_bound`:   Lower bounds for parameters
        * `u_bound`:   Upper bounds for parameters
        """

        # Define the objective function
        fit_list = [data[self.field] for data in data_list]
        def obj_func(params):
            prd_list = [self.model(data, *params) for data in data_list]
            sqr_err  = [(f-p)**2 for f, p in zip(fit_list, prd_list)]
            return np.average(sqr_err)

        # # Quickly optimise
        # arguments = list(inspect.signature(self.model).parameters.keys())
        # init_params = [1.0]*(len(arguments)-1)
        # from scipy.optimize import minimize
        # results = minimize(obj_func, init_params, method="L-BFGS-B")
        # self.opt_params = list(results.x)

        # Define MOGA parameters
        num_gens   = 1000
        population = 100
        offspring  = 100
        crossover  = 0.8
        mutation   = 0.01

        # Define algorithm
        algorithm = NSGA2(
            pop_size     = population,
            n_offsprings = offspring,
            crossover    = SBX(prob=crossover, prob_var=1.0),
            mutation     = PolynomialMutation(prob=mutation),
            eliminate_duplicates = True
        )

        # Define problem
        class Problem(ElementwiseProblem):
            def __init__(self):
                super().__init__(n_var=len(l_bound), n_obj=1, xl=l_bound, xu=u_bound)
            def _evaluate(self, params, out, *args, **kwargs) -> None:
                out["F"] = obj_func(params)
        problem = Problem()
        results = minimize(problem, algorithm, ("n_gen", num_gens), verbose=False, seed=None)

        # Identify optimal parameters
        opt_array = results.X
        opt_array = opt_array[0] if opt_array.ndim == 2 else opt_array
        self.opt_params = list(opt_array)

        # Return
        return round_sf(self.opt_params, 5)

    def plot_1to1(self, cal_data_list:list, val_data_list:list,
                  params:list=None, limits:tuple=None, exp:int=None) -> None:
        """
        Creates a 1-to-1 plot

        Parameters:
        * `cal_data_list`: List of calibration datasets
        * `val_data_list`: List of validation datasets
        * `params`:        List of parameters
        * `limits`:        Define limits for the plot
        * `exp`:           The exponent to scale the ticks
        """
    
        # Get parameters
        params = self.opt_params if params == None else params
        
        # Get all calibration and validation data
        cal_fit_list, cal_prd_list = self.evaluate_2(cal_data_list, params)
        val_fit_list, val_prd_list = self.evaluate_2(val_data_list, params)

        # Define limits if undefined
        if limits == None:
            combined_list = cal_fit_list + cal_prd_list + val_fit_list + val_prd_list
            limits = (min(combined_list), max(combined_list))

        # Initialise plot
        field_info = FIELD_INFO_DICT[self.field]
        create_1to1(field_info["label"], field_info["units"], limits, exp)

        # Plot data for each temperature
        # for temp, marker in zip([800, 900, 1000], ["^", "s", "*"]):
        for temp, marker in zip([0.8, 0.9, 1.0], ["^", "s", "*"]):
            cal_data_sublist = [cd for cd in cal_data_list if cd["temperature"] == temp]
            val_data_sublist = [vd for vd in val_data_list if vd["temperature"] == temp]
            cal_fit_sublist, cal_prd_sublist = self.evaluate_2(cal_data_sublist, params)
            val_fit_sublist, val_prd_sublist = self.evaluate_2(val_data_sublist, params)
            plot_1to1(cal_fit_sublist, cal_prd_sublist, CAL_COLOUR, marker)
            plot_1to1(val_fit_sublist, val_prd_sublist, VAL_COLOUR, marker)
        
        # Plot LOBFs
        lobf_1to1(cal_fit_list, cal_prd_list, CAL_COLOUR, limits)
        lobf_1to1(val_fit_list, val_prd_list, VAL_COLOUR, limits)

        # Add legend for temperatures
        bbox_pos = (0.0, 0.835)
        t800  = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="800°C",  marker="^", s=10**2)
        t900  = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="900°C",  marker="s", s=10**2)
        t1000 = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="1000°C", marker="*", s=10**2)
        legend = plt.legend(handles=[t800, t900, t1000], framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left", bbox_to_anchor=bbox_pos)
        plt.gca().add_artist(legend)
        
        # Save plot
        save_plot(f"results/{self.model_name}.png")

    def get_are(self, data_list:list, params:list=None) -> float:
        """
        Calculates the average relative errors

        Parameters:
        * `data_list`: List of datasets
        * `params`:    List of parameters
        
        Returns the average relative error
        """
        params = self.opt_params if params == None else params
        fit_list, prd_list = self.evaluate_2(data_list, params)
        are = np.average([abs((f-p)/f) for f, p in zip(fit_list, prd_list)])
        return f"{round_sf(are, 5)*100}%"

    def evaluate_2(self, data_list:list, params:list) -> tuple:
        """
        Evaluates the model and scales the outputs

        Parameters:
        * `data_list`: List of data dictionaries
        * `params`:    List of parameters

        Returns the fitting and predicted lists
        """
                
        # Get calibration and validation data
        fit_list = [data[self.field] for data in data_list]
        prd_list = self.evaluate(data_list, params)
        
        # Scale data
        field_info = FIELD_INFO_DICT[self.field]
        scale = lambda x_list : [x*field_info["scale"] for x in x_list]
        fit_list = scale(fit_list)
        prd_list = scale(prd_list)
        
        # Return
        return fit_list, prd_list

    def evaluate(self, data_list:list, params:list) -> list:
        """
        Evaluates the model

        Parameters:
        * `data_list`: List of data dictionaries
        * `params`:    List of parameters

        Returns the model's outputs
        """
        if params == None:
            raise ValueError("Parameters have not been defined or optimised!")
        prd_list = [self.model(data, *params) for data in data_list]
        return prd_list
    
def get_model(model_name:str):
    """
    Gets the model

    Parameters:
    * `model_name`: The name of the model

    Returns the model
    """

    # Check if model exists
    model_names = [name for name, _ in inspect.getmembers(models_, inspect.isfunction)]
    if not model_name in model_names:
        raise ValueError(f"No model named '{model_name}'!")

    # Return model
    model = getattr(models_, model_name, None)
    return model
