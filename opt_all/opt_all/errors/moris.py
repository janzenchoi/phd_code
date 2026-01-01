"""
 Title:         The misorientations objective function
 Description:   The objective function for minimising the misorientations between two
                reorientation trajectories
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from opt_all.errors.__error__ import __Error__
from opt_all.helper.interpolator import Interpolator
from opt_all.maths.orientation import get_cubic_misorientation

# The Misorientations class
class Error(__Error__):
    
    def initialise(self, eval_x_list:list):
        """
        Runs at the start, once
        
        Parameters:
        * `eval_x_list`: The values to evaluate the misorientations
        """
        
        # Get experimental data
        self.labels = self.get_labels()
        exp_x_list = self.get_data(self.labels[0])
        
        # Interpolate experimental orientations
        exp_itp_list = []
        for label in self.labels[1:]:
            exp_phi_list = self.get_data(label)
            exp_itp = Interpolator(exp_x_list, exp_phi_list, len(exp_phi_list))
            exp_itp_list.append(exp_itp)
        
        # Calculate experimental orientations at target strain values
        self.eval_x_list = eval_x_list
        self.exp_phi_list = []
        for eval_x in self.eval_x_list:
            exp_phi = [exp_itp.evaluate([eval_x])[0] for exp_itp in exp_itp_list]
            self.exp_phi_list.append(exp_phi)

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        
        # Get predicted data
        prd_x_list = prd_data[self.labels[0]]
        
        # Interpolate predicted orientations
        prd_itp_list = []
        for label in self.labels[1:]:
            prd_phi_list = prd_data[label]
            prd_itp = Interpolator(prd_x_list, prd_phi_list, len(prd_phi_list))
            prd_itp_list.append(prd_itp)
            
        # Calculate predicted orientations at target strain values
        prd_phi_list = []
        for eval_x in self.eval_x_list:
            prd_phi = [prd_itp.evaluate([eval_x])[0] for prd_itp in prd_itp_list]
            prd_phi_list.append(prd_phi)
        
        # Calculate misorientations
        moris = [get_cubic_misorientation(exp_phi, prd_phi)
                 for exp_phi, prd_phi in zip(self.exp_phi_list, prd_phi_list)]
        avg_mori = np.average(moris)
        return avg_mori
        