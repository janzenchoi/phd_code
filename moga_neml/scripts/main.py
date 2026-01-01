"""
 Title:         Calibration of an EVP model with large strain
 Description:   Interface for calibrating NEML models
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
from moga_neml.interface import Interface
from moga_neml.drivers.large_strain import ls_tensile_driver

def main():
    """
    Main function
    """
    # Define the interface and model
    itf = Interface("evpwdb 800C bt area10", input_path="data", output_path="results")
    itf.define_model("evpwdb")

    # Add short-term creep data
    # itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
    # itf.remove_damage()
    # itf.add_error("area", "time", "strain")

    # itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
    # itf.remove_damage()
    # itf.add_error("area", "time", "strain")

    # Add long-term creep data
    # itf.read_data("creep/inl_1/AirBase_800_65_G33.csv")
    # itf.remove_damage(0.1, 0.7)
    # itf.read_data("creep/inl_1/AirBase_800_60_G32.csv")
    # itf.remove_damage(0.1, 0.7)

    # Add tensile data
    itf.read_data("tensile/inl/AirBase_800_D7.csv")
    itf.get_data("strain_rate")
    itf.add_error("area", "strain", "stress", weight=10)
    # itf.add_error("yield_point", yield_stress=189) # 189MPa @ 800C, 163MPa @ 900C, 90MPa @ 1000C
    itf.add_error("end", "strain")
    itf.add_error("end", "stress")
    # itf.remove_manual("strain", 0.3)
    # itf.add_error("end_more", "strain")

    # Apply driver
    itf.set_custom_driver(
        driver_type = ls_tensile_driver,
        strain_rate = itf.get_data("strain_rate"),
        temperature = itf.get_data("temperature"),
        max_strain  = 0.5
    )

    # Define error reduction methods
    itf.reduce_errors("square_average")
    itf.reduce_objectives("square_average")

    # Conduct optimisation
    itf.plot_experimental()
    itf.set_recorder(10, plot_opt=True, plot_loss=True)
    itf.optimise(10000, 100, 50, 0.8, 0.01)

# Calls the main function
if __name__ == "__main__":
    main()
