"""
 Title:         SR model
 Description:   Symbolic regression model
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from osfem.models.__model__ import __Model__
from osfem.general import csv_to_dict, dict_to_stdout, round_sf

# Model class
class Model(__Model__):

    def initialise(self, file_paths):
        """
        Runs at the start, once
        """
        self.add_param("i", r"$i$", 0, 1e6)
        self.data_dict_list = []
        for file_path in file_paths:
            raw_dict = csv_to_dict(file_path)
            unique = list(set([key.split("_")[0] for key in raw_dict.keys()]))
            data_dict = dict(zip(unique, [[] for _ in range(len(unique))]))
            for key in raw_dict.keys():
                for u in unique:
                    if u in key:
                        data_dict[u] += round_sf(raw_dict[key], 5)
                        break
            self.data_dict_list.append(data_dict)
            # dict_to_stdout(data_dict)

    def evaluate(self, i) -> float:
        """
        Evaluates the model

        Parameters:
        * `...`: Parameters
        
        Returns the response
        """
        data_dict = self.data_dict_list[i]
        field = [field for field in data_dict.keys() if not field in ["stress", "temperature"]][0]
        s = self.get_field("stress")
        t = self.get_field("temperature")
        for j in range(len(data_dict[field])):
            if data_dict["stress"][j] == s and data_dict["temperature"][j] == t:
                # return data_dict[field][j]
                return np.exp(data_dict[field][j])
        return None
