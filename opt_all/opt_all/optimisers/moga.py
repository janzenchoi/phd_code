"""
 Title:         Multi-Objective Genetic Algorithm
 Description:   For parameter optimisation
 Author:        Janzen Choi

"""

# Libraries
import warnings, numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from opt_all.optimisers.__optimiser__ import __Optimiser__

# The MOGA Class
class Optimiser(__Optimiser__):

    def initialise(self, num_gens:int=100, population:int=100, offspring:int=50,
                   crossover:float=0.80, mutation:float=0.01) -> None:
        """
        Initialises the multi-objective genetic algorithm

        Parameters:
        * `num_gens`:  The number of generations to run the MOGA
        * `population`:  The size of the initial population
        * `offspring`: The size of the offspring
        * `crossover`: The crossover probability
        * `mutation`:  The mutation probability
        """

        # Define inputs
        self.num_gens   = num_gens
        self.population = population
        self.offspring  = offspring
        self.crossover  = crossover
        self.mutation   = mutation

        # Gets information about the parameters
        self.fix_param_dict   = self.get_fixed_params()
        self.init_param_dict  = self.get_inited_params()
        self.bind_param_dict  = self.get_bound_params()
        self.unfix_param_list = self.get_unfixed_params()

        # Define algorithm
        self.algo = NSGA2(
            pop_size     = population,
            n_offsprings = offspring,
            sampling     = self.get_population(),
            crossover    = SBX(prob=crossover, prob_var=1.0), # simulated binary crossover 
            mutation     = PolynomialMutation(prob=mutation), # polynomial mutation
            eliminate_duplicates = True
        )

        # Define bounds
        big_bounds = (1e-50, 1e50)
        l_bounds = [self.bind_param_dict[param_name][0] if param_name in self.bind_param_dict.keys()
                    else big_bounds[0] for param_name in self.unfix_param_list]
        u_bounds = [self.bind_param_dict[param_name][1] if param_name in self.bind_param_dict.keys()
                    else big_bounds[1] for param_name in self.unfix_param_list]

        # Define problem
        self.problem = Problem(
            n_var = len(self.unfix_param_list),
            n_obj = len(self.get_error_groups()),
            xl    = np.array(l_bounds),
            xu    = np.array(u_bounds),
            calculate_errors = self.calculate_errors
        )
    
    def get_population(self) -> tuple:
        """
        Given a set of parameters, returns a population with some deviation
        """

        # Determine mean and std values
        mean_list, stdev_list = [], []
        for param_name in self.unfix_param_list:
            if param_name in self.init_param_dict.keys():
                mean_list.append(self.init_param_dict[param_name])
                stdev_list.append(abs(0.01*self.init_param_dict[param_name]))
            elif param_name in self.bind_param_dict.keys():
                mid_point = (self.bind_param_dict[param_name][1] + self.bind_param_dict[param_name][0]) / 2
                bound_range = self.bind_param_dict[param_name][1] - self.bind_param_dict[param_name][0]
                mean_list.append(mid_point)
                stdev_list.append(bound_range/4) # std ~= range / 4
            else:
                mean_list.append(0)
                stdev_list.append(0)

        # Create the population
        param_population = np.random.normal(
            loc   = np.array(mean_list),
            scale = np.array(stdev_list),
            size  = (self.population, len(self.unfix_param_list)),
        )
        
        # Clamp the population by the bounds
        for i in range(len(param_population)):
            for j, param_name in enumerate(self.unfix_param_list):
                bounds = self.bind_param_dict[param_name]
                param_population[i][j] = max(min(param_population[i][j], bounds[1]), bounds[0])
        
        # Return the population
        return param_population

    def optimise(self) -> None:
        """
        Runs the optimisation
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            minimize(self.problem, self.algo, ("n_gen", self.num_gens+1), verbose=False, seed=None)

# Problem class
class Problem(ElementwiseProblem):

    def __init__(self, n_var:int, n_obj:int, xl:np.array, xu:np.array, calculate_errors):
        """
        Initialise the MOGA problem

        Parameters:
        * `n_var`: The number of variables to find
        * `n_obj`: The number of objective functions to optimise
        * `xl`:    The lower bounds
        * `xu`:    The upper bounds
        * `calculate_errors`: The function handler for calculating the errors
        """
        self.calculate_errors = calculate_errors
        super().__init__(n_var=n_var, n_obj=n_obj, xl=xl, xu=xu)

    def _evaluate(self, params:tuple, out:dict, *args, **kwargs) -> None:
        """
        Minimises expression "F" such that the expression "G <= 0" is satisfied

        Parameters:
        * `params`: A list of the parameter values
        * `out`:    The dictionary to attach the error values
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            errors = self.calculate_errors(*params)
            out["F"] = list(errors.values())
