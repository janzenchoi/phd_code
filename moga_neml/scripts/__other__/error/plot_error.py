"""
 Title:         Error plotter
 Description:   Creates plots for looking at the errors of the simulations
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import sys; sys.path += ["../../../"]
from moga_neml.drivers.driver import Driver
from moga_neml.optimise.curve import Curve
from moga_neml.models.evpcd import Model as EVPCD
from moga_neml.models.evpwdb import Model as EVPWD
from moga_neml.errors.__error__ import create_error

# Constants
MODEL_INDEX  = int(sys.argv[1])
DATA_PATH    = "../../data"
MODEL_NAME   = "evpcd" if MODEL_INDEX == 0 else "evpwd"
MODEL        = [EVPCD(MODEL_NAME), EVPWD(MODEL_NAME)][MODEL_INDEX]
TEMP_LIST    = [800, 900, 1000]
MARKER_LIST    = ["^", "s", "*"]
MARKER_SIZE  = 10
LINEWIDTH    = 1
TRANSPARENCY = 0.2

# Parameters
PARAMS_STR = {
    0: {
        "opt": [
            """
            23.304	276.66	0.32123	4.2592	1767.2	2168.5	5.3181	6.7619
            """,
            """
            3.6262	13.804	6.9825	4.2416	1138.2	1986	4.4408	9.193
            """,
            """
            0.31556	4.9177	4.2816	4.8134	468.63	3308.8	3.3387	5.7804
            """,
        ], "oth": [
            # """
            # 16.994	187.83	0.26104	4.502	1784.8	3263.5	4.9231	13.172
            # 22.454	66.77	0.92681	4.4191	1610.1	2142	5.4844	11.449
            # 19.125	43.641	5.6148	4.1688	1616	1876.8	5.5594	6.8653
            # 31.647	120.62	0.85485	3.7266	2297.8	2165.7	5.3247	7.7724
            # 33.297	522.85	0.11871	3.9767	1762.4	1913.8	5.6638	11.287
            # 15.042	35.437	8.4	3.9586	2283.5	4184.6	4.4257	6.6603
            # 24.889	44.932	1.2076	4.5055	1527.9	2589.7	5.1066	8.695
            # 30.401	34.817	4.5983	3.5323	2583	2520.9	5.1559	8.5891
            # 5.0569	40.476	10.017	4.1585	1730.1	1998.1	5.5564	10.337
            # """,
            # """
            # 11.112	18.959	5.9505	3.6368	1471.6	2064.3	4.3164	7.225
            # 11.394	13.887	7.532	3.5691	1581.2	1959.8	4.4121	8.5847
            # 5.6656	7.6357	9.1337	4.3001	1055.4	3494.5	3.9629	11.623
            # 8.0846	21.623	4.9985	3.8734	1330.8	2586.3	4.0925	6.8218
            # 8.7008	379.67	0.15739	4.2166	994.53	1533.4	4.6802	7.0461
            # 9.344	45.972	2.5375	3.4094	1902	2101.5	4.3022	6.1081
            # 16.257	181.45	0.5026	3.0154	2606.2	2445.1	4.1307	5.6964
            # 6.4694	149.62	0.29611	4.1942	1123.8	2045.9	4.4272	9.5323
            # 7.9997	25.008	2.2597	4.127	1102.2	1841.7	4.5535	10.206
            # """,
            # """
            # 0.0046173	6.8476	2.2387	4.8326	460.38	2357.9	3.5989	6.8922
            # 3.1901	126.5	0.16925	3.8924	802.2	2253.9	3.6876	11.145
            # 0.26189	37.662	0.20134	4.8079	478.84	2939.9	3.4262	5.9609
            # 1.5332	6.9652	4.9491	4.3072	551.01	1467.1	4.0639	13.561
            # 0.18711	42.057	1.22	3.9495	803.58	1759.6	3.8088	6.9718
            # 3.4416	6.259	1.314	4.0782	707.11	4504.6	3.2162	8.2904
            # 4.5325	14.166	2.2205	3.8813	731.02	2379.1	3.5504	6.0315
            # 3.3203	95.748	0.45552	4.0634	574.87	1034.8	4.2291	6.0322
            # 4.0855	246.68	0.084526	3.9321	776.2	2681.7	3.4426	5.5305
            # """
        ]
    },
    1: {
        "opt": [
            """
            22.154	462.34	0.17408	4.314	1828.1	40.1	260.65	408.44	853.65	1.9241	7.7562
            """,
            """
            6.3647	183.42	0.44712	4.1839	1075.3	27.326	165.15	422.54	849.67	2.2181	10.568
            """,
            """
            0.2367	39.667	1.2775	4.4023	559.5	9.3449	62.201	262.65	587.44	2.0144	8.7398
            """,
        ], "oth": [
            # """
            # 15.532	158.4	0.53509	4.4223	1866.2	38.705	252.32	356.78	743.33	1.9693	12.056
            # 5.6925	67.1	1.8542	4.7721	1621.6	72.41	404.77	243.19	619.93	2.4798	11.411
            # 19.2	52.605	1.542	4.5105	1614.6	42.528	267.95	334.54	705.42	2.4141	9.9943
            # 31.327	105.29	0.8549	3.7256	2576.7	54.271	333.56	307.45	694.47	1.9991	6.8035
            # 11.45	53.135	7.1795	3.9502	2205.4	30.864	224.62	340.9	729.26	1.3505	6.6858
            # 17.982	81.509	0.84105	4.509	1673.3	39.98	258.79	402.01	829.72	2.2452	8.533
            # 24	301.54	0.32008	4.2863	1836.9	23.714	176.69	323.4	686.91	1.6048	13.085
            # 27.852	31.391	9.837	3.6958	2458	31.947	224.92	521.29	982.66	1.5924	18.309
            # 29.914	48.373	2.3508	3.9615	2094.7	27.335	200.15	367.9	765.16	1.639	19.667
            # """,
            # """							
            # 5.82	16.046	8.3648	4.1595	1064.7	38.773	222.24	393.28	859.75	2.3825	4.5047
            # 11.616	16.725	6.3631	3.6491	1303.7	40.805	222.15	829.14	644.22	3.2018	1.2554
            # 9.8394	12.026	14.017	3.7429	1275	36.916	211.85	498.46	952.62	2.4338	11.505
            # 5.7368	8.3864	16.064	4.3916	855.39	33.396	191.41	420.91	779.17	3.6322	8.1479
            # 7.5309	23.5	5.1998	3.862	1374.9	24.858	154.83	511.79	997.24	2.0041	7.9977
            # 4.8239	389.25	0.18435	4.4133	941.87	44.974	248.15	621.83	913.9	2.4338	7.0609
            # 6.6289	48.408	4.0515	3.7586	1383.6	45.15	253.49	553.63	866.98	1.6648	8.7312
            # 16.262	181.79	0.52517	3.0161	2376.6	29.326	172.8	434.17	894.26	2.192	2.8518
            # 7.9872	16.104	7.2157	4.2939	892.7	13.577	93.551	360.21	764.12	1.9879	15.103
            # """,
            # """
            # 0.13199	6.5191	11.588	4.5757	530.9	7.2545	51.111	244.85	554.46	1.4924	7.066
            # 3.211	111.3	0.17971	4.0658	797.47	7.4637	50.736	283.99	637.4	1.4863	5.3119
            # 0.013628	19.84	4.4536	4.4892	542.97	7.6866	53.311	281.25	622.97	1.3136	7.8413
            # 1.3829	13.171	6.4312	4.1312	644.36	8.422	55.973	261.83	583.57	1.8614	11.981
            # 3.455	16.732	6.9347	3.865	726.51	8.2554	55.102	253.49	563.13	1.3979	7.9624
            # 2.7525	16.605	1.2867	4.2536	650.11	7.4409	51.438	248.11	562.08	1.554	8.8352
            # 3.7022	24.227	2.4711	3.6321	870.39	8.2223	55.404	257.43	593.35	1.9805	8.9843
            # 2.7156	41.193	0.31274	4.0819	825.7	10.001	64.808	248.52	559.21	1.6577	10.642
            # 3.32	381.2	0.07715	4.1319	716.42	7.8478	53.547	261.99	583.71	1.3314	8.2668
            # """
        ]
    }
}

# Returns a thinned list
def get_thinned_list(unthinned_list:list, density:int) -> list:
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    return [unthinned_list[i] for i in thin_indexes]

# Tries to float cast a value
def try_float_cast(value:str) -> float:
    try:
        return float(value)
    except:
        return value

# Converts CSV data into a curve dict
def get_exp_data_dict(headers:list, data:list) -> dict:
    
    # Get indexes of data
    list_indexes = [i for i in range(len(data[2])) if data[2][i] != ""]
    info_indexes = [i for i in range(len(data[2])) if data[2][i] == ""]
    
    # Create curve
    curve = {}
    for index in list_indexes:
        value_list = [float(d[index]) for d in data]
        value_list = get_thinned_list(value_list, 200)
        curve[headers[index]] = value_list
    for index in info_indexes:
        curve[headers[index]] = try_float_cast(data[0][index])

    # Return curve
    return curve

# Removes data from a curve
def remove_data(exp_data:dict, label:str, value:float=None) -> dict:

    # If the value is none, then don't remove anything
    if value == None:
        return exp_data

    # Create a copy of the curve with empty lists
    new_curve = deepcopy(exp_data)
    for header in new_curve.keys():
        if isinstance(new_curve[header], list) and len(new_curve[header]) == len(exp_data[label]):
            new_curve[header] = []
            
    # Remove data after specific value
    for i in range(len(exp_data[label])):
        if exp_data[label][i] > value:
            break
        for header in new_curve.keys():
            if isinstance(new_curve[header], list) and len(exp_data[header]) == len(exp_data[label]):
                new_curve[header].append(exp_data[header][i])
    
    # Return new data
    return new_curve

# Gets the curve dict given a file path
def get_exp_data(file_path:str) -> dict:
    with open(file_path, "r") as file:
        headers = file.readline().replace("\n","").split(",")
        data = [line.replace("\n","").split(",") for line in file.readlines()]
        exp_data = get_exp_data_dict(headers, data)
        return exp_data

# Adds experimental and simulation data to a list of dictionaries
def add_data_info(info_list:list, params_str:str, model, opt:bool=True) -> list:

    # Get parameters
    params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

    # Iterate through experimental data
    for info in info_list:

        # Get experimental data
        exp_data = get_exp_data(info["path"])
        exp_data = remove_data(exp_data, "time", info["time_end"])
        curve = Curve(exp_data, model)
        model.set_exp_data(exp_data)
        info["exp_data"] = exp_data

        # Iterate through parameters
        for params in params_list:
            calibrated_model = model.calibrate_model(*params)
            driver = Driver(curve, calibrated_model)
            sim_data = driver.run()
            data_label = "opt_data_list" if opt else "oth_data_list"
            info[data_label].append(sim_data)

    # Return list of data information
    return info_list

# Calibration data
info_list_list = [[
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_800_80_G25.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_800_70_G44.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_800_65_G33.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_800_60_G32.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/tensile/inl/AirBase_800_D7.csv",      "time_end": None,     "yield": 291 , "exp_data": None, "opt_data_list": [], "oth_data_list": []},
], [
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_900_36_G22.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_900_31_G50.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_900_28_G45.csv",  "time_end": None,     "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_900_26_G59.csv",  "time_end": 20541924, "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/tensile/inl/AirBase_900_D10.csv",     "time_end": None,     "yield": 164 , "exp_data": None, "opt_data_list": [], "oth_data_list": []},
], [
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_16_G18.csv", "time_end": 7756524,  "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_13_G30.csv", "time_end": 16877844, "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_12_G48.csv", "time_end": 18096984, "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": False, "path": f"{DATA_PATH}/creep/inl_1/AirBase_1000_11_G39.csv", "time_end": 19457424, "yield": None, "exp_data": None, "opt_data_list": [], "oth_data_list": []},
    {"calib": True,  "path": f"{DATA_PATH}/tensile/inl/AirBase_1000_D12.csv",    "time_end": None,     "yield": 90  , "exp_data": None, "opt_data_list": [], "oth_data_list": []},
]]

# Class for getting an error value
class Error:
    
    # Constructor
    def __init__(self, error_name:str, x_label:str="", y_label:str=""):
        self.error_name = error_name
        self.x_label = x_label
        self.y_label = y_label
    
    # Gets the error value
    def get_error(self, exp_data:dict, sim_data:dict, yield_stress=None):
        if self.error_name == "yield_point":
            error = create_error(self.error_name, self.x_label, self.y_label, 1, exp_data, MODEL, yield_stress=yield_stress)
        else:
            error = create_error(self.error_name, self.x_label, self.y_label, 1, exp_data, MODEL)
        value = error.get_value(sim_data)
        return value

# Initialise error information
error_dict_list = [
    {"name": r"$E_{t_f}$",          "type": "creep",   "error": Error("end", "time")},
    {"name": r"$E_{\epsilon_f}$",   "type": "creep",   "error": Error("end", "strain")},
    {"name": r"$E_{\epsilon}$",     "type": "creep",   "error": Error("area", "time", "strain")},
    {"name": r"$E_{\sigma_y}$",     "type": "tensile", "error": Error("yield_point")},
    {"name": r"$E_{\sigma_{UTS}}$", "type": "tensile", "error": Error("max", "stress")},
    {"name": r"$E_{\sigma}$",       "type": "tensile", "error": Error("area", "strain", "stress")},
]

# Calculates the errors
def get_error_value_list(error_dict:dict, info_list:list, opt:bool=True) -> list:
    if info_list == []:
        return []
    data_label = "opt_data_list" if opt else "oth_data_list"
    error = error_dict["error"]
    error_value_list = []
    for i in range(len(info_list[0][data_label])):
        error_value = np.average([error.get_error(info["exp_data"], info[data_label][i], info["yield"])**2 for info in info_list])
        error_value_list.append(error_value)
    return error_value_list

# Initialise plot
plt.figure(figsize=(6, 6))

# Iterate through temperatures
for i in range(len(PARAMS_STR[MODEL_INDEX]["opt"])):

    # Get all data at temperature
    info_list = info_list_list[i]
    oth_info_list = []
    if len(PARAMS_STR[MODEL_INDEX]["oth"]) > i:
        oth_info_list = add_data_info(info_list, PARAMS_STR[MODEL_INDEX]["oth"][i], MODEL, opt=False)
    opt_info_list = add_data_info(info_list, PARAMS_STR[MODEL_INDEX]["opt"][i], MODEL, opt=True)

    # Iterate through errors
    for j in range(len(error_dict_list)):
        error_type = error_dict_list[j]["type"]

        # Plot non-optimal calibration error
        cal_oth_info_list = [info for info in oth_info_list if info["calib"] and info["exp_data"]["type"] == error_type]
        error_value_list = get_error_value_list(error_dict_list[j], cal_oth_info_list, opt=False)
        plt.scatter([j]*len(error_value_list), error_value_list, edgecolor="none", color="green", s=MARKER_SIZE**2, marker=MARKER_LIST[i], alpha=TRANSPARENCY)

        # Plot non-optimal validation error
        val_oth_info_list = [info for info in oth_info_list if not info["calib"] and info["exp_data"]["type"] == error_type]
        error_value_list = get_error_value_list(error_dict_list[j], val_oth_info_list, opt=False)
        plt.scatter([j]*len(error_value_list), error_value_list, edgecolor="none", color="red", s=MARKER_SIZE**2, marker=MARKER_LIST[i], alpha=TRANSPARENCY)

        # Plot optimal calibration error
        cal_opt_info_list = [info for info in opt_info_list if info["calib"] and info["exp_data"]["type"] == error_type]
        error_value_list = get_error_value_list(error_dict_list[j], cal_opt_info_list, opt=True)
        plt.scatter([j]*len(error_value_list), error_value_list, edgecolor="black", color="green", linewidth=LINEWIDTH, s=MARKER_SIZE**2, marker=MARKER_LIST[i])

        # Plot optimal validation error
        val_opt_info_list = [info for info in opt_info_list if not info["calib"] and info["exp_data"]["type"] == error_type]
        error_value_list = get_error_value_list(error_dict_list[j], val_opt_info_list, opt=True)
        plt.scatter([j]*len(error_value_list), error_value_list, edgecolor="black", color="red", linewidth=LINEWIDTH, s=MARKER_SIZE**2, marker=MARKER_LIST[i])

# Add legend for data type
cal = plt.scatter([], [], color="green", label="Calibration", s=MARKER_SIZE**2)
val = plt.scatter([], [], color="red", label="Validation", s=MARKER_SIZE**2)
legend = plt.legend(handles=[cal, val], framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=15, loc="upper right")
plt.gca().add_artist(legend)

# Add legend for temperature
t800  = plt.scatter([], [], color="none", edgecolor="black", linewidth=LINEWIDTH,  label="800°C",  marker="^", s=MARKER_SIZE**2)
t900  = plt.scatter([], [], color="none", edgecolor="black", linewidth=LINEWIDTH,  label="900°C",  marker="s", s=MARKER_SIZE**2)
t1000 = plt.scatter([], [], color="none", edgecolor="black", linewidth=LINEWIDTH,  label="1000°C", marker="*", s=MARKER_SIZE**2)
legend = plt.legend(handles=[t800, t900, t1000], framealpha=1, edgecolor="black", fancybox=True, facecolor="white", fontsize=15,
                    loc="upper left", bbox_to_anchor=(0.66,0.85))
plt.gca().add_artist(legend)

# Format tick positions and font
plt.xticks(fontsize=18)
plt.yticks(fontsize=15)
plt.xlim(-0.5, len(error_dict_list)-0.5)
plt.ylim(0, 0.25)
# plt.ylim(1e-5, 1e2)
# plt.yscale("log")

# Format grid and labels
label_pos = np.arange(len(error_dict_list))
plt.gca().set_xticks(label_pos)
plt.xticks(label_pos, [error_dict["name"] for error_dict in error_dict_list])
for x in np.arange(len(error_dict_list)):
    plt.gca().axvline(x=x+0.5, linestyle="-", color="gray", linewidth=0.5)
plt.grid(axis="y", which="major", linestyle="-", color="gray", linewidth=0.5)

# Tighten and save
plt.tight_layout()
plt.savefig(f"plot_{MODEL_NAME}.png")
