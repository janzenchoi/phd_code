"""
 Title:         Spreadsheet Writer
 Description:   Writes results into a spreadsheet
 Author:        Janzen Choi

"""

# Libraries
import pandas as pd
from moga_neml.helper.experiment import get_units

# Spreadsheet class
class Spreadsheet:
    
    def __init__(self, results_path:str):
        """
        Class for interacting with spreadsheets

        Parameters:
        * `results_path`: The path to the spreadsheet
        """
        self.writer = pd.ExcelWriter(results_path, engine="xlsxwriter")
    
    def write_data(self, data_dict:dict, sheet_name:str) -> None:
        """
        Writes a dictionary of lists to a sheet with nice formatting

        Parameters:
        * `data_dict`:  The dictionary of data to be written
        * `sheet_name`: The name of the sheet to be written to
        """

        # Convert dictionary to dataframe
        columns = list(data_dict.keys())
        data = zip_longest([data_dict[column] for column in columns])
        data = list(map(list, zip(*data)))
        dataframe = pd.DataFrame(data, columns=columns)
        
        # Apply fit column widths and write
        dataframe.style.apply(centre_align, axis=0).to_excel(self.writer, sheet_name, index=False)
        sheet = self.writer.sheets[sheet_name]
        for column in dataframe:
            column_length = max(dataframe[column].astype(str).map(len).max(), len(column)) + 1
            column_index = dataframe.columns.get_loc(column)
            sheet.set_column(column_index, column_index, column_length)
    
    def write_plot(self, data_dict_dict:dict, sheet_name:str, x_label:str,
                   y_label:str, plot_type:str) -> None:
        """
        Writes data and the associated plot given a dictionary of dictionaries;
        dictionary requires 'x', 'y', 'size', and 'colour' keys
        
        Parameters:
        * `data_dict_dict`: A dictionary of data dictionaries
        * `sheet_name`:     The name of the sheet to be written to
        * `x_label`:        The label for the x axis
        * `y_label`:        The label for the y axis
        * `plot_type`:      The type of the data to be plotted
        """

        # Convert dictionary of dictionary into list of lists
        data_list_list = []
        for data_name in data_dict_dict.keys():
            data_dict = data_dict_dict[data_name]
            if len(data_dict[x_label]) == 0 or len(data_dict[y_label]) == 0:
                continue
            data_list_list += [data_dict[x_label], data_dict[y_label]]
        
        # Convert data into pandas' desired 
        data_list_list = zip_longest(data_list_list)
        data_list_map = list(map(list, zip(*data_list_list)))
        pd.DataFrame(data_list_map).to_excel(self.writer, sheet_name, index=False)
        
        # Add sheet to spreadsheet and create chart
        sheet = self.writer.sheets[sheet_name]
        chart = self.writer.book.add_chart({"type": plot_type})
        
        # Add converted data to a chart
        for i in range(len(data_dict_dict.keys())):
            data_dict = data_dict_dict[list(data_dict_dict.keys())[i]]
            marker_style = {
                "type":   "circle",
                "size":   data_dict["size"],
                "border": {"color": data_dict["colour"]},
                "fill":   {"color": data_dict["colour"]},
            }
            chart.add_series({
                "name":       list(data_dict_dict.keys())[i],
                "categories": [sheet_name, 1, i*2, len(data_dict[x_label]), i*2],
                "values":     [sheet_name, 1, i*2+1, len(data_dict[x_label]), i*2+1],
                "marker":     marker_style
            })
        
        # Add axes and add the chart to the sheet
        if len(data_dict_dict.keys()) == 1:
            chart.set_legend({"none": True})
        x_units = get_units(x_label)
        y_units = get_units(y_label)
        chart.set_x_axis({"name": f"{x_label}{x_units}", "major_gridlines": {"visible": True}})
        chart.set_y_axis({"name": f"{y_label}{y_units}", "major_gridlines": {"visible": True}})
        sheet.insert_chart("A1", chart)

    # Closes the writer
    def close(self):
        self.writer.close()

def centre_align(x:int) -> list:
    """
    Centre aligns the cells
    
    Parameters:
    * `x`: The elements to apply the alignment to

    Returns a list of the centre alignment text
    """
    return ["text-align: center" for _ in x]

def zip_longest(list_list:list) -> list:
    """
    Imitates zip longest but for a list of lists

    Parameters:
    * `list_list`: A list of lists

    Returns the zipped list of lists
    """
    max_values = max([len(list) for list in list_list])
    new_list_list = []
    for list in list_list:
        new_list = list + [None] * (max_values - len(list))
        new_list_list.append(new_list)
    return new_list_list
