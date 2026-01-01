import sys; sys.path += [".."]
from osfem.data import get_creep, split_data_list
from osfem.plotter import prep_plot, save_plot, lobf_1to1, set_limits, add_legend, CAL_COLOUR, VAL_COLOUR
import matplotlib.pyplot as plt
import numpy as np

data_list = get_creep("data")
data_list = [data.update({"stress": data["stress"]/80}) or data for data in data_list]
data_list = [data.update({"temperature": data["temperature"]/1000}) or data for data in data_list]
cal_data_list, val_data_list = split_data_list(data_list)

get_ln_mcr = lambda data_list : [np.log(data["mcr"]) for data in data_list] # 1/s
get_1dT = lambda data_list : [1/data["temperature"] for data in data_list]
get_s = lambda data_list : [data["stress"] for data in data_list]
get_ln_s = lambda data_list : [np.log(data["stress"]) for data in data_list]
get_ln_ttf = lambda data_list : [np.log(data["ttf"]) for data in data_list]
get_stf = lambda data_list : [data["stf"] for data in data_list]
get_mcr_ttf = lambda data_list : [data["mcr"]*data["ttf"] for data in data_list]

def plot_data(get_x, get_y):
    
    symbol_dict = {0.8: "^", 0.9: "s", 1.0: "*"}
    for data in cal_data_list+val_data_list:
        x_list = get_x([data])
        y_list = get_y([data])
        symbol = symbol_dict[data["temperature"]]
        colour = CAL_COLOUR if data["fit"] else VAL_COLOUR
        plt.scatter(x_list, y_list, color=colour, edgecolor="black", linewidth=1, marker=symbol, s=8**2)

    cal_x_list = get_x(cal_data_list)
    cal_y_list = get_y(cal_data_list)
    val_x_list = get_x(val_data_list)
    val_y_list = get_y(val_data_list)

    buffer = 0.2
    cal_range = abs(max(cal_x_list)-min(cal_x_list))
    cal_limits = (min(cal_x_list)-cal_range*buffer, max(cal_x_list)+cal_range*buffer)
    val_range = abs(max(val_x_list)-min(val_x_list))
    val_limits = (min(val_x_list)-val_range*buffer, max(val_x_list)+val_range*buffer)
    lobf_1to1(cal_y_list, cal_x_list, CAL_COLOUR, cal_limits)
    lobf_1to1(val_y_list, val_x_list, VAL_COLOUR, val_limits)

    handles = [plt.scatter([], [], c=CAL_COLOUR, edgecolor="black", label="Calibration", s=8**2), 
               plt.scatter([], [], c=VAL_COLOUR, edgecolor="black", label="Validation", s=8**2)]
    legend = plt.legend(handles=handles, ncol=1, framealpha=1, edgecolor="black",
                        fancybox=True, facecolor="white", fontsize=12, loc="upper left")
    plt.gca().add_artist(legend)

    bbox_pos = (0.0, 0.835)
    t800  = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="800°C",  marker="^", s=10**2)
    t900  = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="900°C",  marker="s", s=10**2)
    t1000 = plt.scatter([], [], color="none", edgecolor="black", linewidth=1, label="1000°C", marker="*", s=10**2)
    legend = plt.legend(handles=[t800, t900, t1000], framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=12, loc="upper left", bbox_to_anchor=bbox_pos)
    plt.gca().add_artist(legend)

prep_plot(r"$\ln(\hat{\sigma})$", r"$\ln(\dot{\epsilon}_{m})$")
plot_data(get_ln_s, get_ln_mcr)
set_limits((-2.5, 0.5), (-20, -15))
save_plot("results/exp_1.png")

prep_plot(r"$1/\hat{T}$", r"$\ln(\dot{\epsilon}_{m})$")
plot_data(get_1dT, get_ln_mcr)
set_limits((0.9, 1.4), (-20, -15))
save_plot("results/exp_2.png")

prep_plot(r"$\ln(\dot{\epsilon}_{m})$", r"$\ln(t_{f})$")
plot_data(get_ln_mcr, get_ln_ttf)
set_limits((-21, -15), (14, 20))
save_plot("results/exp_3.png")

prep_plot(r"$\ln(\hat{\sigma})$", r"$\ln(t_{f})$")
plot_data(get_ln_s, get_ln_ttf)
set_limits((-2.5, 0.5), (14, 20))
save_plot("results/exp_4.png")

prep_plot(r"$1/\hat{T}$", r"$\ln(t_{f})$")
plot_data(get_1dT, get_ln_ttf)
set_limits((0.9, 1.4), (14, 20))
save_plot("results/exp_5.png")

prep_plot(r"${\epsilon}_{f}$", r"$\dot{\epsilon}_{m}\cdot{t}_{f}$")
plot_data(get_stf, get_mcr_ttf)
set_limits((0, 0.6), (0, 0.35))
save_plot("results/exp_6.png")
