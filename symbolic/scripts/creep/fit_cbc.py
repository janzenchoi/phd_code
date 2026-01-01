"""
 Title:         Fit characteristic-based creep models
 Description:   Script to run symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += ["../.."]
from symbolic.interface import Interface
import numpy as np

# Modelling parameters
TARGET = "mcr"
CAL_ALL = False

# Factors
STRESS_FACTOR = 1/80
TEMPERATURE_FACTOR = 1/1000

def main():
    """
    Main function
    """

    # Initialise
    itf = Interface(f"cbc_{TARGET}_log", input_path="../data", output_path="../results")
    itf.define_model("cbc", target=TARGET)

    # Define scale functions
    scale_stress = lambda s_list : s_list
    scale_temperature = lambda t_list : t_list
    # scale_stress = lambda s_list : [s*STRESS_FACTOR for s in s_list]
    # scale_temperature = lambda t_list : [t*TEMPERATURE_FACTOR for t in t_list]
    scale_target = lambda t_list : [np.log(t) for t in t_list]

    # Add calibration data
    itf.add_data("cal_cbc.csv", True, weight=1.0)
    itf.change_field("stress", scale_stress)
    itf.change_field("temperature", scale_temperature)
    itf.change_field(TARGET, scale_target)
    itf.add_data("val_cbc.csv", CAL_ALL, weight=0.01)
    itf.change_field("stress", scale_stress)
    itf.change_field("temperature", scale_temperature)
    itf.change_field(TARGET, scale_target)

    # Fit the model
    itf.fit_model()

    # Export fit
    itf.export_fit(
        fields    = ["temperature", "stress", TARGET],
        file_name = "data_fit",
    )

    # Get results
    itf.run_model_function("export_errors", data_list=itf.__controller__.get_data_list())
    itf.run_model_function("save_equation")
    itf.plot_equation()

    # Analyse predictions
    func = lambda fd, sd : (fd[TARGET], sd[TARGET])
    itf.plot_1to1(func, TARGET, TARGET, file_name="1to1")

# Calls the main function
if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for i in range(iters):
        main()
