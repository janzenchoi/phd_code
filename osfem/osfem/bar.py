"""
 Title:         Bar
 Description:   Bar plotter
 Author:        Janzen Choi

"""

# Libraries
from osfem.general import round_sf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Parameters
CAL_COLOUR = "tab:green"
VAL_COLOUR = "tab:red"
BAR_WIDTH = 0.35
BAR_DISTANCE = 0.0

def plot_bar(data_grid:list, limits:tuple=None, label:str="", x_ticks:list=None) -> None:
    """
    Creates a bar plot
    
    Parameters:
    * `data_grid`: List of list of data points
    * `limits`:    Limits for the axes
    * `label`:     Label for the y-axis
    * `x_ticks`:   Ticks for the x-axis
    """

    # Initialise plot
    plt.figure(figsize=(5,5), dpi=200)
    # plt.figure(figsize=(6.2,5), dpi=200)
    plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
    plt.gca().grid(which="major", axis="y", color="SlateGray", linewidth=1, linestyle=":", alpha=0.5)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    for spine in plt.gca().spines.values():
        spine.set_linewidth(2)
    
    # Define limits
    if limits != None:
        plt.ylim(limits)
    md = (1-2*BAR_WIDTH-BAR_DISTANCE)/2
    plt.xlim(-md, len(data_grid)+md)

    # Draw bar graphs
    for i, data_list in enumerate(data_grid):

        # Plot bars
        settings = {"zorder": 3, "width": BAR_WIDTH, "edgecolor": "black"}
        bar_cal = plt.bar([i+md+BAR_WIDTH/2], [data_list[0]], color=CAL_COLOUR, **settings)
        bar_val = plt.bar([i+md+3*BAR_WIDTH/2+BAR_DISTANCE], [data_list[1]], color=VAL_COLOUR, **settings)

        # # Add text
        # for bar, colour in zip(bar_cal+bar_val, [CAL_COLOUR, VAL_COLOUR]):
        #     height = round_sf(bar.get_height(), 3)
        #     plt.text(bar.get_x() + bar.get_width()/2, height + (0.02 * plt.ylim()[1]), height, ha="center", va="bottom", fontsize=10, color=colour)
    
    # Add legend
    handles = [
        mpatches.Patch(facecolor=CAL_COLOUR, edgecolor="black", label="Calibration"),
        mpatches.Patch(facecolor=VAL_COLOUR, edgecolor="black", label="Validation"),
    ]
    legend = plt.legend(handles=handles, framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left")
    plt.gca().add_artist(legend)

    # Format axes
    # x_list = list(range(len(data_grid)+1))
    # plt.xticks(ticks=x_list, labels=["" for _ in x_list])
    x_list = [x+0.5 for x in range(len(data_grid))]
    plt.xticks(ticks=x_list, labels=x_ticks)
    # plt.xticks(ticks=x_list, labels=x_ticks, fontsize=11)
    # if x_ticks != None:
    #     plt.gca().set_xticks([x+0.5 for x in x_list], x_ticks)
    plt.ylabel(label, fontsize=14)
