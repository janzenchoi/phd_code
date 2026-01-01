"""
 Title:         The yield objective function
 Description:   The objective function for minimising the discrepancies between the
                yield points of tensile curves
 Author:        Janzen Choi

 """

# Libraries
import math, numpy as np
import scipy.interpolate as inter
import scipy.optimize as opt
from moga_neml.errors.__error__ import __Error__
from moga_neml.optimise.controller import BIG_VALUE

# The Error class
class Error(__Error__):
    
    def initialise(self, yield_stress:float=None, offset:float=0.002):
        """
        Runs at the start, once

        Parameters:
        * `yield_stress`: The yield stress
        * `offset`:       The strain offset to calculate the yield stress
        """

        # Initialisation
        self.enforce_data_type("tensile")
        exp_data = self.get_exp_data()
        self.offset = offset
        
        # Get yield point manually or automatically, based on user input
        if yield_stress != None:
            idx = np.searchsorted(exp_data["stress"], yield_stress)
            idx = np.clip(idx, 1, len(exp_data["stress"])-1)
            x1, x2 = exp_data["strain"][idx - 1], exp_data["strain"][idx]
            y1, y2 = exp_data["stress"][idx - 1], exp_data["stress"][idx]
            yield_strain = x1 + (x2 - x1) * (yield_stress - y1) / (y2 - y1)
            self.exp_yield = (yield_strain, yield_stress)
        else:
            self.exp_yield = get_yield(exp_data["strain"], exp_data["stress"], self.offset)
        self.mag_yield = math.sqrt(math.pow(self.exp_yield[0], 2) + math.pow(self.exp_yield[1], 2))

    # Computes the error value
    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        try:
            prd_yield = get_yield(prd_data["strain"], prd_data["stress"], self.offset)
        except ValueError:
            return BIG_VALUE
        distance = math.sqrt(math.pow(self.exp_yield[0] - prd_yield[0], 2) + math.pow(self.exp_yield[1] - prd_yield[1], 2))
        return distance / self.mag_yield
        # return abs((prd_yield[1] - self.exp_yield[1]) / self.exp_yield[1])

def get_yield(strain_list:list, stress_list:list, offset:float=0.002) -> tuple:
    """
    Calculates the yield strain and stress

    Parameters:
    * `strain_list`: The list of strain values
    * `stress_list`: The list of stress values
    * `offset`:      The offset used to determine the yield point

    Returns the yield strain and stress
    """
    youngs = stress_list[1] / strain_list[1] # NEML produces noiseless curves
    sfn = inter.interp1d(strain_list, stress_list, bounds_error=False, fill_value=0)
    tfn = lambda e: youngs * (e - offset)
    yield_strain = opt.brentq(lambda e: sfn(e) - tfn(e), 0.0, np.max(strain_list))
    yield_stress = float(tfn(yield_strain))
    return yield_strain, yield_stress
