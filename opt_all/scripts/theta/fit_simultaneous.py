import sys; sys.path += ["../.."]
from opt_all.helper.general import flatten
from opt_all.interface import Interface

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

# Initialise model
itf = Interface(f"theta_simultaneous", input_path="../data", output_path="../results")
itf.define_model("theta/simultaneous")

# Bind parameters
for i in [1,2,3,4]:
    itf.bind_param(f"a{i}", -1e2, 1e2)
    itf.bind_param(f"b{i}", -2e2, 2e2)
    itf.bind_param(f"c{i}", -1e2, 1e2)
    itf.bind_param(f"d{i}", -2e2, 2e2)

# Initialise parameters
param_names = flatten([[f"{pn}{i}" for pn in "abcd"] for i in "1234"])
param_values_str = "-1.0418	-26.501	-4.8193	35.371	4.2914	-5.7226	-2.3207	7.2026	18.55	18.587	-19.688	-30.372	-11.647	-2.9601	11.474	7.7091"
param_values = [float(pv) for pv in param_values_str.split("	")]
for pn, pv in zip(param_names, param_values):
    itf.init_param(pn, pv)

# Iterate through the data
for i, data in enumerate(DATA_LIST):

    # Add data
    itf.read_data(data["path"])
    
    # Remove oxidation
    if data["ox"] != None:
        itf.remove_after("time", data["ox"])

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
    if data["fit"]:
        itf.add_error("area", labels=["time", "strain"], group=f"area_{i}")
        # itf.add_error("end", labels=["strain"], group="end")

# Set up recorder
itf.start_recorder(interval=10000)
for temperature in [800, 900, 1000]:
    itf.record_plot(
        x_field    = "time",
        y_field    = "strain",
        x_scale    = 1/3600,
        x_units    = "h",
        y_units    = "mm/mm",
        y_limits   = (0, 1.0),
        file_name  = f"plot_fit_{temperature}",
        conditions = {"temperature": temperature/1000}
    )

# Optimise
itf.optimise("moga", num_gens=10000, population=1000, offspring=1000, crossover=0.8, mutation=0.01)
