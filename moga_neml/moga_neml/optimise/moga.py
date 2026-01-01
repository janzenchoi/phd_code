"""
 Title:         Multi-Objective Genetic Algorithm
 Description:   For parameter optimisation
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
import warnings
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.optimize import minimize
from moga_neml.optimise.problem import Problem

# The Multi-Curve Genetic Algorithm (MOGA) class
class MOGA:
    
    def __init__(self, problem:Problem, num_gens:int, init_pop:int, offspring:int,
                 crossover:float, mutation:float):
        """
        Class for the multi-objective genetic algorithm

        Parameters:
        * `problem`:   The problem to optimise
        * `num_gens`:  The number of generations to run the optimiser
        * `init_pop`:  The size of the initial population
        * `offspring`: The size of the offspring
        * `crossover`: The crossover probability
        * `mutation`:  The mutation probability
        """

        # Initialise
        self.problem    = problem
        self.controller = problem.get_controller()
        self.param_dict = self.controller.get_unfix_param_dict()
        self.num_gens   = num_gens
        self.init_pop   = init_pop
        self.offspring  = offspring
        self.crossover  = crossover
        self.mutation   = mutation

        # Gets initialised parameters
        init_param_dict = self.controller.get_init_param_dict()
        population = self.get_population(init_param_dict)

        # Define algorithm
        self.algo = NSGA2(
            pop_size     = init_pop,
            n_offsprings = offspring,
            sampling     = population,
            crossover    = SBX(prob=crossover, prob_var=1.0), # simulated binary crossover 
            mutation     = PolynomialMutation(prob=mutation), # polynomial mutation
            eliminate_duplicates = True
        )

    def get_population(self, init_param_dict:dict) -> tuple:
        """
        Given a set of parameters, returns a population with some deviation

        Parameters:
        * `init_param_dict`: The dictionary of initial parameter values

        Returns a population with the initial parameter values applied
        """

        # Initialise
        mean_list  = []
        stdev_list = []
        
        # Determine mean and std values
        for param_name in self.param_dict.keys():
            
            # If the user defined a starting value
            if param_name in init_param_dict.keys():
                mean_list.append(init_param_dict[param_name])
                stdev_list.append(0.1 * init_param_dict[param_name])
                # stdev_list.append(0)
            
            # Otherwise, define normal sampling
            else:
                mid_point = (self.param_dict[param_name]["u_bound"] + self.param_dict[param_name]["l_bound"]) / 2
                bound_range = self.param_dict[param_name]["u_bound"] - self.param_dict[param_name]["l_bound"]
                mean_list.append(mid_point)
                stdev_list.append(bound_range/4) # std ~= range / 4

        # Create the population
        param_population = np.random.normal(
            loc   = np.array(mean_list),
            scale = np.array(stdev_list),
            size  = (self.init_pop, len(self.param_dict.keys())),
        )
        
        # Clamp the population by the bounds
        for i in range(len(param_population)):
            for j in range(len(self.param_dict.keys())):
                param_name = list(self.param_dict.keys())[j]
                l_bound = self.param_dict[param_name]["l_bound"]
                u_bound = self.param_dict[param_name]["u_bound"]
                param_population[i][j] = max(min(param_population[i][j], u_bound), l_bound)
                
        # Return the population
        return param_population

    def optimise(self) -> None:
        """
        Runs the genetic optimisation
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            minimize(self.problem, self.algo, ("n_gen", self.num_gens), verbose=False, seed=None)
