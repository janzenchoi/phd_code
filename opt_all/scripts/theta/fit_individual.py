import sys; sys.path += ["../.."]
from opt_all.interface import Interface

# Define data
DATA_LIST = [
    {"path": "inl_1/AirBase_800_80_G25.csv",  "tts": 2174580,  "ox": None},
    # {"path": "inl_1/AirBase_800_70_G44.csv",  "tts": 4951332,  "ox": None},
    # {"path": "inl_1/AirBase_800_65_G33.csv",  "tts": 7927344,  "ox": None},
    # {"path": "inl_1/AirBase_800_60_G32.csv",  "tts": 12509442, "ox": None},
    # {"path": "inl_1/AirBase_900_36_G22.csv",  "tts": 2484756,  "ox": None},
    # {"path": "inl_1/AirBase_900_31_G50.csv",  "tts": 5122962,  "ox": None},
    # {"path": "inl_1/AirBase_900_28_G45.csv",  "tts": 6807168,  "ox": None},
    # {"path": "inl_1/AirBase_900_26_G59.csv",  "tts": 10289304, "ox": 20578608},
    # {"path": "inl_1/AirBase_1000_16_G18.csv", "tts": 3883572,  "ox": 7767144},
    # {"path": "inl_1/AirBase_1000_13_G30.csv", "tts": 8448138,  "ox": 16896276},
    # {"path": "inl_1/AirBase_1000_12_G48.csv", "tts": 9102942,  "ox": 18205884},
    # {"path": "inl_1/AirBase_1000_11_G39.csv", "tts": 9765990,  "ox": 19531980},
]

# Iterate through the data
for data in DATA_LIST:

    # Initialise model
    data_info = data["path"].split("/")[-1].split("_")
    itf = Interface(f"theta_{data_info[1]}_{data_info[2]}", input_path="../data", output_path="../results")
    itf.define_model("theta/individual")

    # Bind parameters
    itf.bind_param(f"t1", -5, 1)
    itf.bind_param(f"t2",  0, 10)
    itf.bind_param(f"t3", -5, 1)
    itf.bind_param(f"t4",  0, 10)
    # itf.bind_param(f"t5", -5, 1)
    # itf.bind_param(f"t6",  0, 10)

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
    # itf.add_error("end", labels=["strain"], group="end")

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
    # itf.optimise("moga", num_gens=400, population=1000, offspring=1000, crossover=0.8, mutation=0.01)
    itf.optimise("moga", num_gens=100, population=1000, offspring=1000, crossover=0.8, mutation=0.01)
