"""
 Title:         Plotter
 Description:   For plotting data
 Author:        Janzen Choi
 
"""

# Libraries
import matplotlib.pyplot as plt
import matplotlib.colors as mcolours
import numpy as np

# Constants
DEFAULT_PATH = "./plot"
EXP_COLOUR   = "silver"
CAL_COLOUR   = "tab:green"
VAL_COLOUR   = "tab:red"
ALL_COLOURS  = list(mcolours.TABLEAU_COLORS) + list(mcolours.BASE_COLORS) + list(mcolours.CSS4_COLORS)

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

    def prep_plot(self, title:str="", size:int=14) -> None:
        """
        Prepares the plot
        
        Parameters:
        * `title`: The title of the plot
        * `size`:  The size of the font
        """

        # Set figure size and title
        plt.figure(figsize=(5,5), dpi=200)
        plt.title(title, fontsize=size+3, fontweight="bold", y=1.05)
        plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
        plt.gca().grid(which="major", axis="both", color="SlateGray", linewidth=1, linestyle=":")

        # Set x and y labels
        plt.xlabel(self.x_label.replace('_', ' ').capitalize(), fontsize=size)
        plt.ylabel(self.y_label.replace('_', ' ').capitalize(), fontsize=size)
        
        # Format
        plt.xticks(fontsize=size-2)
        plt.yticks(fontsize=size-2)
        for spine in plt.gca().spines.values():
            spine.set_linewidth(1)
    
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
    
    def scat_plot(self, data_dict:dict, colour:str=CAL_COLOUR, size:int=8, priority:int=1) -> None:
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
        
    def line_plot(self, data_dict:dict, colour=CAL_COLOUR, linewidth:int=3, priority:int=1) -> None:
        """
        Plots the experimental data using a line plot

        Parameters:
        * `data_dict`: The dictionary to store the data
        * `colour`:    The colour to plot the data
        * `priority`:  The priority of the curve
        """
        x_list = data_dict[self.x_label]
        if self.x_label == "time":
            x_list = [x/3600 for x in x_list]
        plt.plot(x_list, data_dict[self.y_label], colour, linewidth=linewidth, zorder=priority)

    def define_legend(self, colour_list:list, label_list:list, size_list:list, type_list:list, **kwargs) -> None:
        """
        Defines the plot legend
        
        Parameters:
        * `colour_list`: The colours in the legend
        * `label_list`:  The keys to add to the legend
        * `size_list`:   The size of the icons in the legend
        * `type_list`:   The type of the icons in the legend
        """
        for i in range(len(colour_list)):
            if type_list[i] == "scatter":
                plt.scatter([], [], color=colour_list[i], label=label_list[i], s=size_list[i]**2)
            elif type_list[i] == "line":
                plt.plot([], [], color=colour_list[i], label=label_list[i], linewidth=size_list[i])
        plt.legend(framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, **kwargs)

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

def define_legend(colour_list:list, label_list:list, type_list:list, **kwargs) -> None:
    """
    Manually defines the plot legend
    
    Parameters:
    * `colour_list`: The colours in the legend
    * `label_list`:  The keys to add to the legend
    * `type_list`:   The type of the icons in the legend
    """
    for i in range(len(colour_list)):
        if type_list[i] == "scatter":
            plt.scatter([], [], color=colour_list[i], label=label_list[i], s=7**2)
        elif type_list[i] == "line":
            plt.plot([], [], color=colour_list[i], label=label_list[i], linewidth=2)
    plt.legend(framealpha=1, edgecolor="black", fancybox=True, facecolor="white", **kwargs)

def save_plot(file_path:str) -> None:
    """
    Saves the plot and clears the figure

    Parameters:
    * `file_path`: The path to save the plot
    """
    plt.savefig(file_path)
    plt.cla()
    plt.clf()
    plt.close()

def set_limits(x_limits:tuple=None, y_limits:tuple=None) -> None:
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

def prep_plot(x_label:str, y_label:str, x_units:str="", y_units:str="", title:str="", size:int=14) -> None:
    """
    Prepares the plot
    
    Parameters:
    * `x_label`: Label for the x-axis
    * `y_label`: Label for the y-axis
    * `x_units`: Units for the x-axis
    * `y_units`: Units for the y-axis
    * `title`:   The title of the plot
    * `size`:    The size of the font
    """

    # Set figure size and title
    plt.figure(figsize=(5,5), dpi=200)
    plt.title(title, fontsize=size+3, fontweight="bold", y=1.05)
    plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
    plt.gca().grid(which="major", axis="both", color="SlateGray", linewidth=1, linestyle=":", alpha=0.5)

    # Set x and y labels
    x_unit_str = f" ({x_units})" if x_units != "" else ""
    y_unit_str = f" ({y_units})" if y_units != "" else ""
    plt.xlabel(f"{x_label}{x_unit_str}", fontsize=size)
    plt.ylabel(f"{y_label}{y_unit_str}", fontsize=size)
    
    # Format
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    for spine in plt.gca().spines.values():
        spine.set_linewidth(2)

def add_legend(calibration:bool=True, validation:bool=True) -> None:
    """
    Adds a basic legend

    Parameters:
    * `calibration`: Whether to add calibration to the legend
    * `validation`:  Whether to add validation to the legend
    """
    handles = [plt.scatter([], [], color=EXP_COLOUR, label="Experiment",  s=8**2)]
    if calibration:
        handles += [plt.plot([], [], color=CAL_COLOUR, label="Calibration", linewidth=3)[0]]
    if validation:
        handles += [plt.plot([], [], color=VAL_COLOUR, label="Validation", linewidth=3)[0]]
    legend = plt.legend(handles=handles, ncol=1, framealpha=1, edgecolor="black",
                        fancybox=True, facecolor="white", fontsize=12, loc="upper left")
    plt.gca().add_artist(legend)

def create_1to1(label:str, units:str, limits:tuple) -> None:
    """
    Plots a 1:1 comparison

    Parameters:
    * `label`:  Label to represent values
    * `units`:  Units to place beside label
    * `limits`: Limits of the plot
    """

    # Initialise figure    
    prep_plot(f"Simulated {label}", f"Measured {label}", units, units)
    plt.gca().set_aspect("equal", "box")
    set_limits(limits, limits)

    # Add 'conservative' region
    triangle_vertices = np.array([[limits[0], limits[0]], [limits[1], limits[0]], [limits[1], limits[1]]])
    plt.gca().fill(triangle_vertices[:, 0], triangle_vertices[:, 1], color="gray", alpha=0.3)
    plt.text(limits[1]-0.48*(limits[1]-limits[0]), limits[0]+0.05*(limits[1]-limits[0]), "Non-conservative", fontsize=12, color="black")
    plt.plot([limits[0], limits[1]], [limits[0], limits[1]], color="black", linestyle="--", linewidth=1)

    # Define legend
    ch = plt.scatter([], [], color=CAL_COLOUR, edgecolor="black", linewidth=1, label="Calibration", marker="o", s=10**2, zorder=3)
    vh = plt.scatter([], [], color=VAL_COLOUR, edgecolor="black", linewidth=1, label="Validation",  marker="o", s=10**2, zorder=3)
    handles = [ch, vh]
    legend = plt.legend(handles=handles, ncol=1, framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left")
    plt.gca().add_artist(legend)

    # Determine tick scale
    max_magnitude = max([abs(limit) for limit in limits])
    exp = np.floor(np.log10(max_magnitude))

    # Scale ticks
    plt.gca().ticklabel_format(axis="x", style="sci", scilimits=(exp,exp))
    plt.gca().ticklabel_format(axis="y", style="sci", scilimits=(exp,exp))
    plt.gca().xaxis.major.formatter._useMathText = True
    plt.gca().yaxis.major.formatter._useMathText = True

def plot_1to1(fit_list:list, prd_list:list, colour:str, marker:str="o") -> None:
    """
    Plots data on the 1-to-1 plot

    Parameters:
    * `fit_list`: The fitting data
    * `prd_list`: The predicted data
    * `colour`:   The colour of the markers
    * `marker`:   The type of markers
    """
    plt.scatter(prd_list, fit_list, zorder=3, edgecolor="black", color=colour, linewidth=1, s=10**2, marker=marker)

def lobf_1to1(fit_list:list, prd_list:list, colour:str, limits:tuple) -> None:
    """
    Plots the LOBF on the 1-to-1 plot

    Parameters:
    * `fit_list`: The fitting data
    * `prd_list`: The predicted data
    * `colour`:   The colour of the LOBF
    * `limits`:   Limits of the plot
    """
    x_list = [limits[0], limits[1]]
    lobf_m, lobf_b = np.polyfit(prd_list, fit_list, 1)
    y_list = [lobf_m*x + lobf_b for x in x_list]
    plt.plot(x_list, y_list, color=colour, linewidth=2, linestyle="--", zorder=2)
