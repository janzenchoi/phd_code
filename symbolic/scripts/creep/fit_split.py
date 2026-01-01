"""
 Title:         Main
 Description:   Script to run symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from symbolic.interface import Interface
from symbolic.helper.derivative import differentiate_curve
from symbolic.helper.interpolator import intervaluate

# Data information
CAL_ALL = False
DATA_LIST = [
    {"path": "creep/inl_1/AirBase_800_80_G25.csv",  "fit": True,    "tts": 2174580,  "ox": None},
    {"path": "creep/inl_1/AirBase_800_70_G44.csv",  "fit": True,    "tts": 4951332,  "ox": None},
    {"path": "creep/inl_1/AirBase_800_65_G33.csv",  "fit": CAL_ALL, "tts": 7927344,  "ox": None},
    {"path": "creep/inl_1/AirBase_800_60_G32.csv",  "fit": CAL_ALL, "tts": 12509442, "ox": None},
    {"path": "creep/inl_1/AirBase_900_36_G22.csv",  "fit": True,    "tts": 2484756,  "ox": None},
    {"path": "creep/inl_1/AirBase_900_31_G50.csv",  "fit": True,    "tts": 5122962,  "ox": None},
    {"path": "creep/inl_1/AirBase_900_28_G45.csv",  "fit": CAL_ALL, "tts": 6807168,  "ox": None},
    {"path": "creep/inl_1/AirBase_900_26_G59.csv",  "fit": CAL_ALL, "tts": 10289304, "ox": 20578608},
    {"path": "creep/inl_1/AirBase_1000_16_G18.csv", "fit": True,    "tts": 3883572,  "ox": 7767144},
    {"path": "creep/inl_1/AirBase_1000_13_G30.csv", "fit": True,    "tts": 8448138,  "ox": 16896276},
    {"path": "creep/inl_1/AirBase_1000_12_G48.csv", "fit": CAL_ALL, "tts": 9102942,  "ox": 18205884},
    {"path": "creep/inl_1/AirBase_1000_11_G39.csv", "fit": CAL_ALL, "tts": 9765990,  "ox": 19531980},
]

# Factors
STRESS_FACTOR = 1/80
TEMPERATURE_FACTOR = 1/1000
TIME_FACTOR = 1#/25018884

# Primary expressions
PRIMARY = "((x2 + -0.15243843) ^ 24.897495) * (((((x1 ^ 4.9040275) * 0.07466753) + 5.3023064e-6) * (x0 ^ 0.7891348)) + -0.2275761)"
# PRIMARY = "(x1 * -0.006332761) + ((x2 ^ 27.50187) * (((x0 * 2.5089362e-6) + ((x0 ^ 0.6898817) * ((x1 ^ 4.4354463) + -0.00028588227))) * 0.0029725276))"
# PRIMARY = "(((x0 ^ 0.72372866) * (((x1 ^ 4.5520124) * 0.00207779) + 1.6697571e-7)) + -0.0077864355) * (x2 ^ 28.33268)"
# PRIMARY = "x1 * (((((((x1 ^ 0.12369788) * x2) + -0.73472077) * 27.641317) ^ 2.7547991) * (x0 * 6.9134147e-9)) ^ 0.7480784)"
# PRIMARY = "((((x2 ^ 6.1973977) * x1) * 2.3468797) ^ (2.403753 + ((1.0878402e7 / (x0 + 396887.84)) ^ 0.6066912))) * 1.9023632"

def main(primary:str):
    """
    Main function

    Parameters:
    * `primary`: The julia expression for the primary creep
    """

    # Initialise
    itf = Interface("split st", input_path="../data", output_path="../results")
    itf.define_model("creep_split", julia=primary)

    # Add data
    for data in DATA_LIST:

        # Add data and partition
        itf.add_data(data["path"], fitting=data["fit"], weights=[1,2,4,8])
        if data["ox"] != None:
            itf.remove_after("time", data["ox"])

        # Scale the data
        itf.change_field("stress", lambda s : s*STRESS_FACTOR)
        itf.change_field("temperature", lambda t : t*TEMPERATURE_FACTOR)
        itf.change_field("time", lambda t_list : [t*TIME_FACTOR for t in t_list])

    # Fit the model
    itf.fit_model()

    # Run model-specific functions
    itf.run_model_function("export_errors", data_list=itf.__controller__.get_data_list())
    itf.run_model_function("save_equation")

    # Save the results
    for temperature in [800, 900, 1000]:
        itf.plot_fit(
            x_field    = "time",
            y_field    = "strain",
            x_scale    = TIME_FACTOR/3600,
            x_units    = "h",
            y_units    = "mm/mm",
            y_limits   = (0, None),
            file_name  = f"plot_fit_{temperature}",
            conditions = {"temperature": temperature*TEMPERATURE_FACTOR},
        )
    itf.export_fit(["time", "strain"])
    itf.plot_equation()

    # Analyse strain predictions
    def strains(fd:dict, sd:dict) -> tuple:
        cttf = min([max(fd["time"]), max(sd["time"])])
        t_list = [(i+1)*cttf/10 for i in range(10)]
        fd_strains = intervaluate(fd["time"], fd["strain"], t_list)
        sd_strains = intervaluate(sd["time"], sd["strain"], t_list)
        return fd_strains, sd_strains
    itf.plot_1to1(strains, r"$\epsilon$", "mm/mm", file_name="1to1_strains")
    
    # Analyse time-to-failure predictions
    ttf = lambda fd, sd : ([max(fd["time"])], [max(sd["time"])])
    itf.plot_1to1(ttf, r"${t}_{f}$", "mm/mm", file_name="1to1_ttf")
    
    # Analyse strain-to-failure predictions
    stf = lambda fd, sd : ([max(fd["strain"])], [max(sd["strain"])])
    itf.plot_1to1(stf, r"${\epsilon}_{f}$", "mm/mm", file_name="1to1_stf")
    
    # Analyse minimum creep rate predictions
    get_mcr = lambda dd : min(differentiate_curve(dd, "time", "strain")["strain"])
    mcr = lambda fd, sd : ([get_mcr(fd)], [get_mcr(sd)])
    itf.plot_1to1(mcr, r"$\dot{\epsilon}_{min}$", "1/s", file_name="1to1_mcr")

# Calls the main function
if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for i in range(iters):
        main(PRIMARY)
