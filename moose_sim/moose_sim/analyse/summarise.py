"""
 Title:         Summarise
 Description:   Analysis functions for simulation results
 Author:        Janzen Choi

"""

# Libraries
import os, numpy as np
from moose_sim.helper.general import round_sf, flatten
from moose_sim.helper.io import csv_to_dict
from moose_sim.maths.orientation import get_average_quat
from moose_sim.maths.neml import moose_quat_to_euler

def get_csv_results(results_path:str, include:str=None, exclude:str=None) -> list:
    """
    Gets the results

    Parameters:
    * `results_path`: Path to the results
    * `include`:      Keyword to identify files to include
    * `exclude`:      Keyword to identify files to exclude

    Returns the results as a list of dictionaries
    """
    csv_file_list  = [csv_file for csv_file in os.listdir(results_path)
                      if csv_file.endswith(".csv") and (include == None or include in csv_file)
                      and (include == None or not exclude in csv_file)]
    csv_file_list  = sorted(csv_file_list)
    data_dict_list = [csv_to_dict(f"{results_path}/{csv_file}") for csv_file in csv_file_list]
    return data_dict_list

def get_block_ids(data_dict:dict, block_id_field:str) -> list:
    """
    Gets the block IDs
    
    Parameters:
    * `data_dict`:      The dictionary of the data
    * `block_id_field`: The field for the block IDs
    
    Returns the list of block IDs
    """
    return [int(block_id) for block_id in list(set(data_dict[block_id_field]))]

def map_field(data_dict:dict, source_field:str, target_field:str, source_include:list=None) -> dict:
    """
    Maps a field to another field

    Parameters:
    * `data_dict`:      The dictionary of the data
    * `source_field`:   The field to conduct the mapping from
    * `target_field`:   The field to conduct the mapping to
    * `source_include`: The values to include in the mapping;
                        includes all values if undefined

    Returns the mapping as a dictionary of lists of values
    """

    # Initialise mapping
    source_values = source_include if source_include != None else data_dict[source_field] 
    source_values = set(source_values)
    map_dict = dict(zip(source_values, [[] for _ in range(len(source_values))]))

    # Conduct mapping and return
    for i, source_value in enumerate(data_dict[source_field]):
        if source_value in source_values:
            target_value = data_dict[target_field][i]
            map_dict[source_value].append(target_value)
    return map_dict

def get_average_field(data_dict_list:list, target_field:str, block_map:dict) -> list:
    """
    Gets a list of averaged values

    Parameters:
    * `data_dict_list`: The list of dictionaries of data
    * `target_field`:   The field to conduct the mapping to
    * `block_map`:      The dictionary mapping the block IDs to element IDs

    Returns a list of averaged values for each dictionary of simulation results
    """
    element_set = set(flatten(block_map.values()))
    average_list = []
    for data_dict in data_dict_list:
        target_values = [data_dict[target_field][i] for i in range(len(data_dict[target_field]))
                         if data_dict["id"][i] in element_set]
        average_list.append(np.average(target_values))
    return average_list

def get_fields(data_dict:dict, source_field:str, target_fields:list, source_include:list=None) -> list:
    """
    Gets the values for a certain field

    Parameters:
    * `data_dict`:      The dictionary of the data
    * `source_field`:   The field to conduct the mapping from
    * `target_fields`:  The fields to conduct the mapping to
    * `source_include`: The values to include in the mapping;
                        includes all values if undefined

    Returns the list of lists of values
    """

    # Initialise source values
    source_values = source_include if source_include != None else data_dict[source_field] 
    source_values = set(source_values)

    # Get target values and return
    target_values_list = []
    for i, source_value in enumerate(data_dict[source_field]):
        if source_value in source_values:
            target_values = [data_dict[target_field][i] for target_field in target_fields]
            target_values_list.append(target_values)
    return target_values_list

def map_average_field(data_dict_list:list, target_field:str, block_map:dict, weight_field:str=None) -> dict:
    """
    Maps the block IDs to the average values of a field

    Parameters:
    * `data_dict_list`: The list of dictionaries of data
    * `target_field`:   The field to conduct the mapping to
    * `block_map`:      The dictionary mapping the block IDs to element IDs
    * `weight_field`:   The field to weight the orientations; doesn't weight if undefined

    Returns a dictionary mapping the block IDs to the averaged values
    """
    
    # Initialise
    block_ids = list(block_map.keys())
    average_dict = dict(zip(block_ids, [[] for _ in range(len(block_ids))]))

    # Iterate through data dictionaries
    for data_dict in data_dict_list:
        for block_id in block_ids:
            
            # Get target field
            target_value_list = get_fields(data_dict, "id", [target_field], block_map[block_id])
            target_value_list = flatten(target_value_list)
            
            # Get weight list if defined
            if weight_field == None:
                weight_list = [1]*len(target_value_list)
            else:
                weight_list = get_fields(data_dict, "id", [weight_field], block_map[block_id])
                weight_list = flatten(weight_list)
                weight_list = [1]*len(weight_list) if sum(weight_list) == 0 else weight_list
            
            # Get average based on weights
            average_value = np.average(target_value_list, weights=weight_list)
            average_dict[block_id].append(round_sf(average_value, 5))
    
    # Return
    return average_dict

def map_total_field(data_dict_list:list, target_field:str, block_map:dict) -> dict:
    """
    Maps the block IDs to the sum of values of a field

    Parameters:
    * `data_dict_list`: The list of dictionaries of data
    * `target_field`:   The field to conduct the mapping to
    * `block_map`:      The dictionary mapping the block IDs to element IDs

    Returns a dictionary mapping the block IDs to the totaled values
    """
    
    # Initialise
    block_ids = list(block_map.keys())
    total_dict = dict(zip(block_ids, [[] for _ in range(len(block_ids))]))

    # Iterate through data dictionaries
    for data_dict in data_dict_list:
        for block_id in block_ids:
            target_value_list = get_fields(data_dict, "id", [target_field], block_map[block_id])
            target_value_list = flatten(target_value_list)
            total_value = sum(target_value_list)
            total_dict[block_id].append(round_sf(total_value, 5))
    
    # Return
    return total_dict

def get_average_euler(data_dict_list:list, orientation_fields:list, block_map:dict,
                      weight_field:str=None, offset:bool=True) -> dict:
    """
    Gets the average orientations from a block map

    Parameters:
    * `data_dict_list`:     The list of dictionaries of orientation data
    * `orientation_fields`: The list of fields for the orientations (quaternions)
    * `block_map`:          The dictionary mapping the block IDs to element IDs
    * `weight_field`:       The field to weight the orientations; doesn't weight if undefined
    * `offset`:             Whether to offset the angle at the t=0
    
    Returns a dictionary mapping the block ID to a list of average orientations (euler-bunge, rads) 
    """

    # Initialise
    block_ids = list(block_map.keys())
    average_dict = dict(zip(block_ids, [[] for _ in range(len(block_ids))]))

    # Store average orientations
    for i, data_dict in enumerate(data_dict_list):
        for block_id in block_ids:
            
            # Get the quaternions
            quat_list = get_fields(data_dict, "id", orientation_fields, block_map[block_id])
            
            # Get average quaternions
            if weight_field == None:
                average_quat = get_average_quat(quat_list)
            else:
                weight_list = get_fields(data_dict, "id", [weight_field], block_map[block_id])
                weight_list = flatten(weight_list)
                weight_list = [1]*len(weight_list) if sum(weight_list) == 0 else weight_list
                average_quat = get_average_quat(quat_list, weight_list)
            
            # Convert to euler-bunge angles and append
            average_euler = moose_quat_to_euler(average_quat, reorient=True, offset=(i==0 and offset))
            average_euler = [round_sf(ae, 5) for ae in average_euler]
            average_dict[block_id].append(average_euler)

    # Return mapping
    return average_dict
