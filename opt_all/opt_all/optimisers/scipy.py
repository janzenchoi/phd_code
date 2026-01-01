"""
 Title:         Least Square Algorithm
 Description:   For parameter optimisation
 Author:        Janzen Choi

"""

# Libraries
from scipy.optimize import minimize
from opt_all.optimisers.__optimiser__ import __Optimiser__

# The Least Square Class
class Optimiser(__Optimiser__):

    def initialise(self, solver:str="L-BFGS-B", tolerance:float=1e-6, max_iter:int=1e3) -> None:
        """
        Initialises the least square
        """

        # Initialise
        self.solver    = solver
        self.tolerance = tolerance
        self.max_iter  = max_iter
        unfixed_param_names    = self.get_unfixed_params()
        
        # Define initial guess
        init_param_dict = self.get_inited_params()
        self.inited_list = []
        for param_name in unfixed_param_names:
            if param_name in init_param_dict.keys():
                self.inited_list.append(init_param_dict[param_name])
            else:
                self.inited_list.append(0)

        # Define bounds
        bind_param_dict = self.get_bound_params()
        self.bound_list = []
        for param_name in unfixed_param_names:
            if param_name in bind_param_dict.keys():
                self.bound_list.append(bind_param_dict[param_name])
            else:
                self.bound_list.append((None, None))

    def calculate_errors(self, *params):
        """
        Overrides the calculate_errors function
        """
        params = params[0]
        errors_dict = super().calculate_errors(*params)
        errors_list = list(errors_dict.values())
        reduced_error = self.controller.reduce_errors(errors_list)
        return reduced_error

    def optimise(self) -> None:
        """
        Runs the optimisation
        """
        minimize(self.calculate_errors, self.inited_list, bounds=self.bound_list,
                 tol=self.tolerance, options={"maxiter": self.max_iter}, method=self.solver)
