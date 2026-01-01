import sys; sys.path += ["../.."]
from opt_all.interface import Interface
from opt_all.helper.general import csv_to_dict, dict_to_csv, safe_mkdir
import os, numpy as np, time

# iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1
iters = 10
for _ in range(iters):

    # Define directory
    TIMESTAMP = time.strftime("%y%m%d%H%M%S", time.localtime(time.time()))
    OUTPUT_PATH = f"../results/{TIMESTAMP}_theta_ox"
    safe_mkdir(OUTPUT_PATH)

    # Define data
    CAL_ALL = False
    DATA_LIST = [
        {"path": "inl_1/AirBase_800_80_G25.csv",  "fit": True, "tts": 2174580,  "ox": None},
        {"path": "inl_1/AirBase_800_70_G44.csv",  "fit": True, "tts": 4951332,  "ox": None},
        {"path": "inl_1/AirBase_800_65_G33.csv",  "fit": CAL_ALL, "tts": 7927344,  "ox": None},
        {"path": "inl_1/AirBase_800_60_G32.csv",  "fit": CAL_ALL, "tts": 12509442, "ox": None},
        {"path": "inl_1/AirBase_900_36_G22.csv",  "fit": True, "tts": 2484756,  "ox": None},
        {"path": "inl_1/AirBase_900_31_G50.csv",  "fit": True, "tts": 5122962,  "ox": None},
        {"path": "inl_1/AirBase_900_28_G45.csv",  "fit": CAL_ALL, "tts": 6807168,  "ox": None},
        {"path": "inl_1/AirBase_900_26_G59.csv",  "fit": CAL_ALL, "tts": 10289304, "ox": 20578608},
        {"path": "inl_1/AirBase_1000_16_G18.csv", "fit": True, "tts": 3883572,  "ox": 7767144},
        {"path": "inl_1/AirBase_1000_13_G30.csv", "fit": True, "tts": 8448138,  "ox": 16896276},
        {"path": "inl_1/AirBase_1000_12_G48.csv", "fit": CAL_ALL, "tts": 9102942,  "ox": 18205884},
        {"path": "inl_1/AirBase_1000_11_G39.csv", "fit": CAL_ALL, "tts": 9765990,  "ox": 19531980},
    ]

    # Parameter names
    PARAM_NAMES = ["t1", "t2", "t3", "t4"]

    # Iterate through the data
    for data in DATA_LIST:

        # Initialise model
        data_info = data["path"].split("/")[-1].split("_")
        itf = Interface(f"theta_{data_info[1]}_{data_info[2]}", input_path="../data", output_path=OUTPUT_PATH)
        itf.define_model("theta/individual")

        # Bind parameters
        itf.bind_param(f"t1", -10, 1)
        itf.bind_param(f"t2",  0, 10)
        itf.bind_param(f"t3", -5, 1)
        itf.bind_param(f"t4",  0, 10)

        # Add data
        itf.read_data(data["path"])
        
        # # Remove oxidation
        # if data["ox"] != None:
        #     itf.remove_after("time", data["ox"])

        # Sparsen data
        itf.sparsen_data(100)

        # Normalise time
        data_dict = itf.get_data()
        max_time = max(data_dict["time"])
        time_list = [t/max_time for t in data_dict["time"]]
        itf.change_data("time", time_list)

        # Normalise temperature and stress
        itf.change_data("temperature", data_dict["temperature"]/1000)
        itf.change_data("stress", data_dict["stress"]/80)

        # Add error
        itf.add_error("area", labels=["time", "strain"], group="area")

        # Set up recorder
        itf.start_recorder(interval=20000, export=True)
        itf.record_plot(
            x_field    = "time",
            y_field    = "strain",
            x_scale    = 1/3600,
            x_units    = "h",
            y_units    = "mm/mm",
            y_limits   = (0, 1.0),
            file_name  = f"plot_fit",
        )

        # Optimise
        itf.optimise("moga", num_gens=400, population=1000, offspring=1000, crossover=0.8, mutation=0.01)

    # Initialise
    dir_path_list = os.listdir(OUTPUT_PATH)
    headers = ["stress", "temperature"] + PARAM_NAMES
    cal_dict = dict(zip(headers, [[] for _ in headers]))
    val_dict = dict(zip(headers, [[] for _ in headers]))

    # Iterate through results
    for dir_path, data in zip(dir_path_list, DATA_LIST):

        # Read data
        file_path = f"{OUTPUT_PATH}/{dir_path}/params.csv"
        if not os.path.exists(file_path):
            continue

        # Append test conditions
        data_info = dir_path.split("_")
        if data["fit"]:
            cal_dict["temperature"].append(int(data_info[2])/1000)
            cal_dict["stress"].append(int(data_info[3])/80)
        else:
            val_dict["temperature"].append(int(data_info[2])/1000)
            val_dict["stress"].append(int(data_info[3])/80)

        # Append parameters
        data_dict = csv_to_dict(file_path)
        for pn in PARAM_NAMES:
            param_name = f"Param ({pn})"
            if param_name in data_dict.keys():
                param_value = data_dict[param_name][0]
                if data["fit"]:
                    cal_dict[pn].append(param_value)
                else:
                    val_dict[pn].append(param_value)

    # Save parameters
    dict_to_csv(cal_dict, f"{OUTPUT_PATH}/params_cal.csv")
    dict_to_csv(val_dict, f"{OUTPUT_PATH}/params_val.csv")

    for pn in PARAM_NAMES:

        # Initialise model
        itf = Interface(f"theta_param_{pn}", input_path=OUTPUT_PATH, output_path=OUTPUT_PATH)
        itf.define_model("theta/param", theta_param=pn)

        # Bind parameters
        itf.bind_param("a", -1e2, 1e2)
        itf.bind_param("b", -2e2, 2e2)
        itf.bind_param("c", -1e2, 1e2)
        itf.bind_param("d", -2e2, 2e2)

        # Add calibration data
        itf.read_data("params_cal.csv")
        data_dict = itf.get_data()
        itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])
        itf.add_error("area_1d", labels=[pn])

        # Add validation data
        itf.read_data("params_val.csv")
        data_dict = itf.get_data()
        itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])

        # Set up recorder
        itf.start_recorder(interval=50000)
        itf.record_plot("stress", pn)

        # Optimise
        itf.optimise("moga", num_gens=1000, population=1000, offspring=1000, crossover=0.8, mutation=0.1)
