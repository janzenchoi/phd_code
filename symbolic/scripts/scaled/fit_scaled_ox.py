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
import numpy as np

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

def main():
    """
    Main function
    """

    # Initialise
    itf = Interface("scaled", input_path="../data", output_path="../results")
    itf.define_model("creep_scaled")
    # itf.define_model("creep_scaled_ox")

    # Add data
    for data in DATA_LIST:

        # Add data and partition
        itf.add_data(data["path"], fitting=True, weight=1.0 if data["fit"] else 0.1)
        # itf.add_data(data["path"], fitting=data["fit"])
        # itf.add_data(data["path"], fitting=data["fit"], weights=[1,2,4,8])

        # Scale the data
        itf.change_field("stress", lambda s : s*STRESS_FACTOR)
        itf.change_field("temperature", lambda t : t*TEMPERATURE_FACTOR)
        
        # Account for oxidation
        # if data["ox"] != None:
        #     itf.remove_after("time", data["ox"])
        def include_oxidation(data_dict:dict) -> dict:
            data_dict["ox"] = data["ox"]
            return data_dict
        itf.change_data(include_oxidation)

    # Fit the model
    itf.fit_model()

    # Run model-specific functions
    itf.run_model_function("export_errors", data_list=itf.__controller__.get_data_list())
    itf.run_model_function("save_equation")

    # Save the results
    for temperature in [800, 900, 1000]:

        # Plot curves
        itf.plot_fit(
            x_field    = "time",
            y_field    = "strain",
            x_scale    = 1/3600,
            x_units    = "h",
            y_units    = "mm/mm",
            x_limits   = (0, None),
            y_limits   = (0, None),
            file_name  = f"plot_fit_{temperature}",
            conditions = {"temperature": temperature*TEMPERATURE_FACTOR},
        )

        # Export curves
        for stress in [11, 12, 13, 16, 26, 28, 31, 36, 60, 65, 70, 80]:
            itf.export_fit(
                fields     = ["time", "strain"],
                file_name  = f"data_fit_{temperature}_{stress}",
                conditions = {"temperature": temperature*TEMPERATURE_FACTOR, "stress": stress*STRESS_FACTOR},
            )

    # Plot eequation
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
        main()
