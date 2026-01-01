"""
 Title:         The yield strain objective function
 Description:   The objective function for minimising the discrepancies between the
                yield strain of tensile curves
 Author:        Janzen Choi

 """

# Libraries
import numpy as np
import scipy.interpolate as inter
import scipy.optimize as opt
from opt_all.errors.__error__ import __Error__
from opt_all.optimise.controller import BIG_VALUE

# The Error class
class Error(__Error__):
    
    def initialise(self, yield_strain:float, offset:float=0.002):
        """
        Runs at the start, once

        Parameters:
        * `yield_strain`: The yield strain
        * `offset`:       The strain offset to calculate the yield strain
        """
        self.yield_strain = yield_strain
        self.offset = offset

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
        return abs((self.yield_strain-prd_yield[0])/self.yield_strain)
        
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
