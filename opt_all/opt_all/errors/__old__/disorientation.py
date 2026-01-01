"""
 Title:         The disorientation objective function
 Description:   The objective function for minimising the disorientation between two sets of angles
 Author:        Janzen Choi

"""

# Libraries
from opt_all.errors.__error__ import __Error__
from opt_all.maths.orientation import get_cubic_misorientation

# The Disorientation class
class Error(__Error__):
    
    def initialise(self):
        """
        Runs at the start, once
        """
        exp_data = self.get_exp_data()
        self.exp_end = self.get_x_data()[-1]
        self.exp_euler = [exp_data[label][-1] for label in self.get_labels()[0:]]

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        prd_strain = prd_data[self.get_x_label()]
        prd_euler = []
        for label in self.get_labels()[0:]:
            gradient = (prd_data[label][-1]-prd_data[label][0])/(prd_strain[-1]-prd_strain[0])
            prd_phi = gradient*(self.exp_end-prd_strain[0]) + prd_data[label][0]
            prd_euler.append(prd_phi)
        disorientation = get_cubic_misorientation(self.exp_euler, prd_euler)
        # return disorientation / math.pi
        return disorientation*10
