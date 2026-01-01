# Libraries
import sys; sys.path += [".."]
from osfem.plotter import save_plot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Parameters
EMP_COLOUR = "tab:blue"
SR_COLOUR  = "tab:orange"
BAR_WIDTH = 0.35
BAR_DISTANCE = 0.0

data_grid = [[1.22, 14.49], [1.05, 16.42], [1.19, 15.33], [28.34, 57.46], [31.5, 59.33]]
x_ticks = ["Minimum\ncreep rate", "Time-to-\nfailure", "Strain-to-\nfailure", "Regular\nstrain-time", "Mechanism-\nshifted\nstrain-time"]
limits = (0, 80)
label = "Computational Cost (min)"

# Initialise plot
# plt.figure(figsize=(5,5), dpi=200)
plt.figure(figsize=(6.2,5), dpi=200)
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
    settings = {"zorder": 3, "width": BAR_WIDTH, "edgecolor": "black"}
    bar_cal = plt.bar([i+md+BAR_WIDTH/2], [data_list[0]], color=EMP_COLOUR, **settings)
    bar_val = plt.bar([i+md+3*BAR_WIDTH/2+BAR_DISTANCE], [data_list[1]], color=SR_COLOUR, **settings)

# Add legend
handles = [
    mpatches.Patch(facecolor=EMP_COLOUR, edgecolor="black", label="Empirical"),
    mpatches.Patch(facecolor=SR_COLOUR, edgecolor="black", label="Symbolic Regression"),
]
legend = plt.legend(handles=handles, framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left")
plt.gca().add_artist(legend)

# Format axes
# x_list = list(range(len(data_grid)+1))
# plt.xticks(ticks=x_list, labels=["" for _ in x_list])
x_list = [x+0.5 for x in range(len(data_grid))]
plt.xticks(ticks=x_list, labels=x_ticks, fontsize=11)
plt.ylabel(label, fontsize=14)


save_plot("results/times.png")
