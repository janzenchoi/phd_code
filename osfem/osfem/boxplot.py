"""
 Title:         Plot Params
 Description:   Compares the parameters through boxplots
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from osfem.general import round_sf

# Plotting parameters
# BOXPLOT_COLOUR = (1.0, 0.6, 0.6, 0.5)
OPT_COLOUR     = "tab:green"
BOXPLOT_COLOUR = (0.6, 1.0, 0.6, 0.3)
BOXPLOT_WIDTH  = 0.4
WIDTH_FACTOR   = 0.6
WHITE_SPACE    = 1.5

def plot_boxplots(label_list:list, values_list:list, limits_list:list,
                  opt_index:int, output_path:str, max_size:int=None) -> None:
    """
    Plots parameter distributions

    Parameters:
    * `label_list`:  List of labels
    * `values_list`: List of parameter values
    * `limits_list`: List of limits
    * `opt_index`:   Optimal parameter index
    * `output_path`: Path to the output directory
    * `max_size`:    The maximum size to leave whitespace
    """

    # Identify number of parameters
    num_rows = max_size if max_size != None else len(label_list)
    # _, axes = plt.subplots(nrows=num_rows, ncols=1, figsize=(5, 5), sharex=False, dpi=300)
    # plt.subplots_adjust(bottom=0.12, top=0.87, left=0.1, right=0.67, wspace=WHITE_SPACE, hspace=WHITE_SPACE)
    _, axes = plt.subplots(nrows=num_rows, ncols=1, figsize=(5, 4), sharex=False, dpi=300)
    plt.subplots_adjust(bottom=0.12, top=0.95, left=0.17, right=0.67, wspace=WHITE_SPACE, hspace=WHITE_SPACE)
    
    # Iterate through parameters
    for label, values, limits, axis in zip(label_list, values_list, limits_list, axes):

        # Initialise
        l_bound, u_bound = limits
        opt_value = round_sf(values[opt_index], 5)

        # Determine optimal value position
        if u_bound <= 0:
            x_position = l_bound + (u_bound-l_bound)*1.05
        else:
            x_position = u_bound + (u_bound-l_bound)*0.05

        # Add formatting
        axis.set_ylabel(label, fontsize=14, fontweight="bold", rotation=0, labelpad=18, va="center")
        # axis.set_ylabel(label, fontsize=14, fontweight="bold", rotation=0, labelpad=20, va="center")
        # asterisked = f"${label.replace('$','')}^*$"
        # param_text = f"({asterisked}= {opt_value})"
        param_text = f"({opt_value})"
        axis.text(x_position, 0, param_text, color="black", va="center", ha="left", fontsize=14)
        axis.grid(which="major", axis="both", color="SlateGray", linewidth=2, linestyle=":", alpha=0.5)
        for spine in axis.spines.values():
            spine.set_linewidth(2)

        # Plot boxplots
        linewidth = 1.5
        sns.boxplot(
            x=values, y=[0]*len(values), ax=axis, width=BOXPLOT_WIDTH, showfliers=True, whis=[0, 100],
            boxprops=dict(edgecolor="black", linewidth=linewidth), # set box edge color
            medianprops=dict(color="black", linewidth=linewidth),  # set median line width
            whiskerprops=dict(color="black", linewidth=linewidth), # set whisker line width
            capprops=dict(color="black", linewidth=linewidth),     # set cap line width
            capwidths=[BOXPLOT_WIDTH],
            flierprops=dict(markerfacecolor='r', markersize=3, linestyle='none'),
            orient="h", color=BOXPLOT_COLOUR
        )

        # Plot optimal point
        axis.scatter([opt_value], [0], c=OPT_COLOUR, edgecolor="black", linewidths=linewidth, s=8**2, zorder=3)

        # Determine tick scale
        max_magnitude = max([abs(limit) for limit in limits])
        exp = np.floor(np.log10(max_magnitude))

        # Fromat axis
        axis.set_yticks([])
        # axis.set_xticks(pi["ticks"])
        axis.set_xlim(l_bound, u_bound)
        axis.set_ylim((-0.3, 0.3))
        if not exp in [0, 1]:
            axis.ticklabel_format(axis="x", style="sci", scilimits=(exp,exp))
        axis.xaxis.major.formatter._useMathText = True
        axis.tick_params(axis="x", labelsize=12)
        axis.tick_params(axis="y", labelsize=12)

    # If number of plots is more than the number of parameters
    for i, axis in enumerate(axes):
        if i < len(label_list):
            continue
        axis.set_visible(False)

    # Save
    plt.savefig(output_path)
