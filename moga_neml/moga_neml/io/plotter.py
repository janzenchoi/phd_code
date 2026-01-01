"""
 Title:         Plotter
 Description:   For plotting data
 Author:        Janzen Choi
 
"""

# Libraries
import matplotlib.pyplot as plt
from moga_neml.helper.experiment import get_units

# Constants
DEFAULT_PATH = "./plot"
EXP_COLOUR   = "darkgray"
CAL_COLOUR   = "green"
VAL_COLOUR   = "red"

# Plotter class
class Plotter:

    def __init__(self, path:str=DEFAULT_PATH, x_label:str="x", y_label:str="y"):
        """
        Class for plotting data

        Parameters:
        * `path`:    The path to save the plot
        * `x_label`: The label for the x axis
        * `y_label`: The label for the y axis
        """
        self.path = path
        self.x_label = x_label
        self.y_label = y_label

    def prep_plot(self, title:str="", label_size:int=15, tick_size:int=11) -> None:
        """
        Prepares the plot
        
        Parameters:
        * `title`:       The title of the plot
        * `lable_size`:  The size of the font
        * `tick_size`:   The size of the numbers on the axes
        """

        # Set figure size and title
        plt.figure(figsize=(5,5))
        # plt.title(title, fontsize=label_size, fontweight="bold", y=1.05) # uncomment me
        plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
        plt.gca().grid(which="major", axis="both", color="SlateGray", linewidth=1, linestyle=":")

        # Set x and y labels
        x_units = get_units(self.x_label)
        y_units = get_units(self.y_label)
        plt.xlabel(f"{self.x_label.replace('_', ' ').capitalize()}{x_units}", fontsize=label_size)
        plt.ylabel(f"{self.y_label.replace('_', ' ').capitalize()}{y_units}", fontsize=label_size)
        plt.xticks(fontsize=tick_size)
        plt.yticks(fontsize=tick_size)
    
    def set_limits(self, x_limits:tuple=None, y_limits:tuple=None) -> None:
        """
        Sets the limits of the x and y scales

        Parameters:
        * `x_limits`: The upper and lower bounds of the plot for the x scale
        * `y_limits`: The upper and lower bounds bound of the plot for the y scale
        """
        if x_limits != None:
            plt.xlim(*x_limits)
        if y_limits != None:
            plt.ylim(*y_limits)

    def set_log_scale(self, x_log:bool=False, y_log:bool=False) -> None:
        """
        Changes the scale of the plot
        
        Parameters:
        * `x_log`: Whether to log the x scale
        * `y_log`: Whether to log the y scale
        """
        if x_log:
            plt.xscale("log")
        if y_log:
            plt.yscale("log")
    
    def scat_plot(self, data_dict:dict, colour:str=EXP_COLOUR, size:int=5, priority:int=1) -> None:
        """
        Plots the experimental data using a scatter plot

        Parameters:
        * `data_dict`: The dictionary to store the data
        * `colour`:    The colour to plot the data
        * `size`:      The size of the curve
        * `priority`:  The priority of the curve
        """
        x_list = data_dict[self.x_label]
        if self.x_label == "time":
            x_list = [x/3600 for x in x_list]
        plt.scatter(x_list, data_dict[self.y_label], s=size**2,
                    marker="o", color=colour, linewidth=1, zorder=priority)
        
    def line_plot(self, data_dict:dict, colour:str=VAL_COLOUR, linewidth:float=1, priority:int=1, alpha:float=1.0) -> None:
        """
        Plots the experimental data using a line plot

        Parameters:
        * `data_dict`: The dictionary to store the data
        * `colour`:    The colour to plot the data
        * `linewidth`: The width of the line
        * `priority`:  The priority of the curve
        * `alpha`:     The degree of transparency
        """
        x_list = data_dict[self.x_label]
        if self.x_label == "time":
            x_list = [x/3600 for x in x_list]
        plt.plot(x_list, data_dict[self.y_label], colour, linewidth=linewidth, zorder=priority, alpha=alpha)

    def define_legend(self, colour_list:list, label_list:list, size_list:list, type_list:list, font_size:int=12) -> None:
        """
        Defines the plot legend
        
        Parameters:
        * `colour_list`: The colours in the legend
        * `label_list`:  The keys to add to the legend
        * `size_list`:   The size of the icons in the legend
        * `type_list`:   The type of the icons in the legend
        * 'font_size`:   The size of the legend text
        """
        for i in range(len(colour_list)):
            if type_list[i] == "scatter":
                plt.scatter([], [], color=colour_list[i], label=label_list[i], s=size_list[i]**2)
            elif type_list[i] == "line":
                plt.plot([], [], color=colour_list[i], label=label_list[i], linewidth=size_list[i])
        plt.legend(
            framealpha = 1,
            edgecolor  = "black",
            fancybox   = True,
            facecolor  = "white",
            fontsize   = font_size,
            loc        = "upper right"
        )

    def save_plot(self) -> None:
        """
        Saves the plot
        """
        plt.savefig(self.path)
    
    def clear(self) -> None:
        """
        Clears the plot
        """
        plt.clf()
