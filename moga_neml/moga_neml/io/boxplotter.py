"""
 Title:         Boxplotter
 Description:   For creating boxplots
 Author:        Janzen Choi
 
"""

# Libraries
import matplotlib.pyplot as plt
import seaborn as sns

def plot_boxplots(data_list_list:list, file_path:str, title:str, colour_list:list=None,
                  limits_dict:list=None, log:bool=False, horizontal:bool=True) -> None:
    """
    Creates multiple boxplots

    Parameters:
    * `data_list_list`: A list of datasets (list)
    * `file_path`:      The path to save the boxplots
    * `title`:          The title on top of the boxplots
    * `colour_list`:    A list of colours
    * `limits_dict`:    A dictionary of tuples (i.e., (lower, upper)) defining the scale of the boxplots
    * `log`:            Whether to apply log scale or not
    * `horizontal`:    Whether to plot the boxplots horizontally (or vertically)
    """

    # Create plots
    num_data = len(data_list_list)
    if horizontal:
        fig, axes = plt.subplots(nrows=num_data, ncols=1, figsize=(5, num_data*0.8), sharex=False)
    else:
        fig, axes = plt.subplots(nrows=1, ncols=num_data, figsize=(num_data*1.6, 5), sharex=False)

    # Add horizontal boxplots and data points
    for i, axis in enumerate(axes):

        # Create boxplot
        axis.grid(True)
        data_list = data_list_list[i]
        y_list = [i + 1] * len(data_list)
        if horizontal:
            sns.boxplot(x=data_list, y=y_list, ax=axis, width=0.5, showfliers=False, boxprops=dict(alpha=0.8),
                        color=colour_list[i] if colour_list is not None else None, orient="h")
        else:
            sns.boxplot(x=y_list, y=data_list, ax=axis, width=0.5, showfliers=False, boxprops=dict(alpha=0.8),
                    color=colour_list[i] if colour_list is not None else None, orient="v")

        # Format ticks
        if horizontal:
            axis.tick_params(axis="x", labelsize=14)
            axis.set_yticks([])
            axis.set_ylabel("")
        else:
            axis.tick_params(axis="y", labelsize=14)
            axis.set_xticks([])
            axis.set_xlabel("")

        # Apply limits and log if desired
        if limits_dict != None:
            limits = list(limits_dict.values())[i]
            if horizontal:
                axis.set_xlim(limits)
            else:
                axis.set_ylim(limits)
        if log:
            if horizontal:
                axis.set_xscale("log")
            else:
                axis.set_yscale("log")

    # Format and save figure
    # fig.suptitle(title, fontsize=14, fontweight="bold") # uncomment me
    fig.tight_layout()
    plt.savefig(file_path)
