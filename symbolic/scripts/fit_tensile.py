"""
 Title:         Main
 Description:   Script to run symbolic regression
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
from symbolic.interface import Interface

# Constants
WEIGHTS = [2, 2, 1, 0.5, 0.5, 1]

def main():
    """
    Main function
    """

    # Initialise
    itf = Interface()
    # itf.define_model("single")
    itf.define_model("tensile_tes")

    # Add fitting data
    # itf.add_data("tensile/inl/AirBase_20_D5.csv")
    # itf.add_data("tensile/inl/AirBase_800_D7.csv")
    for file in ["AirBase_800_D7", "AirBase_850_D9", "AirBase_900_D10", "AirBase_950_D11", "AirBase_1000_D12"]:
        itf.add_data(f"tensile/inl/{file}.csv", fitting=True, weights=WEIGHTS)

    # Fit the data
    itf.fit_model()

    # Save the results
    itf.plot_fit(
        x_field = "strain",
        y_field = "stress",
        x_units = "mm/mm",
        y_units = "MPa",
    )
    itf.plot_equation()

    # Analyse results
    stresses = lambda data_dict : [max(data_dict["stress"])*(i+1)/10 for i in range(10)]
    itf.plot_1to1(stresses, r"$\sigma$", "MPa")

# Calls the main function
if __name__ == "__main__":
    main()
