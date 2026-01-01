"""
 Title:         The decreasing end constraint
 Description:   The constraint for ensuring that as stress increases, the end points of a field decreases 
 Author:        Janzen Choi

"""

# Libraries
from moga_neml.constraints.__constraint__ import __Constraint__

# The decreasing end constraint class
class Constraint(__Constraint__):
    
    def check(self, prd_data_list:list) -> bool:
        """
        Checks whether a constraint has been passed or not (must be overridden)
        
        Parameters:
        * `prd_data_list`: List of predicted data dictionaries
        
        Returns the results of the check
        """

        # Initialisation
        curve_list = self.get_curve_list()
        x_label    = self.get_x_label()
        prd_dict   = {}
        
        # Get map of first field to end point of second field
        for i in range(len(prd_data_list)):
            stress = curve_list[i].get_exp_data()["stress"]
            prd_dict[stress] = prd_data_list[i][x_label][-1]

        # Sort the map in ascending order
        sorted_items = sorted(prd_dict.items(), key=lambda x: x[0])
        prd_dict = dict(sorted_items)

        # Enforce that end points decrease as stress increases
        check_passed = True
        min_value = 1.0e50
        for key in prd_dict.keys():
            if prd_dict[key] > min_value:
                check_passed = False
            min_value = prd_dict[key]
        
        # Return outcome
        # print("dec", prd_dict, check_passed)
        return check_passed
