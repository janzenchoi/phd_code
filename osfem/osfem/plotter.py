"""
 Title:         Plotter
 Description:   Plotting functions
 Author:        Janzen Choi
 
"""

# Libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolours

# Constants
EXP_COLOUR = "silver"
CAL_COLOUR = "tab:green"
VAL_COLOUR = "tab:red"

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

def save_plot(file_path:str, settings:dict={}) -> None:
    """
    Saves the plot and clears the figure

    Parameters:
    * `file_path`: The path to save the plot
    * `settings`:  Settings for the `savefig` function
    """
    plt.savefig(file_path, **settings)
    plt.cla()
    plt.clf()
    plt.close()

def lighten_colour(colour:str, factor:float=0.5):
    """
    Lighten a color by mixing it with white
    
    Parameters:
    * `colour`:  A Matplotlib colour (e.g., 'blue', '#FF0000', (1, 0, 0)).
    * `factor`: A number between 0 and 1. Higher values make it lighter.
    
    Returns the lightened colour
    """
    rgb = mcolours.to_rgb(colour)
    white = (1, 1, 1)
    return tuple(factor * w + (1 - factor) * c for c, w in zip(rgb, white))

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

def plot_1to1(fit_list:list, prd_list:list, settings) -> None:
    """
    Plots data on the 1-to-1 plot

    Parameters:
    * `fit_list`: The fitting data
    * `prd_list`: The predicted data
    """
    plt.scatter(prd_list, fit_list, zorder=3, edgecolor="black", linewidth=1, s=10**2, **settings)

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
