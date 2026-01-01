"""
 Title:         Calibration of an EVP model with large strain
 Description:   Interface for calibrating NEML models
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
import sys; sys.path += [".."]
from moga_neml.interface import Interface
from moga_neml.drivers.large_strain import ls_tensile_driver

def main():
    """
    Main function
    """

    # 800C, yield, UTS, ductility
    # print(truify_stress_strain(189, 0.0039859))
    # print(truify_stress_strain(289.5, 0.0738))
    # print(truify_stress_strain(151.2, 0.840))

    # 900C, yield, UTS, ductility
    # print(truify_stress_strain(163, 0.0042399))
    # print(truify_stress_strain(166.2, 0.03888))
    # print(truify_stress_strain(133.0, 0.351))

    # 1000C, yield, UTS, ductility
    # print(truify_stress_strain(90, 0.0051301))
    # print(truify_stress_strain(92.25, 0.0738))
    # print(truify_stress_strain(73.8, 0.394))

    # Define the interface and model
    itf = Interface("test", input_path="data", output_here=True, verbose=False)
    itf.define_model("evpwdb")

    itf.read_data("tensile/inl/AirBase_800_D7.csv")
    itf.read_data("tensile/inl/AirBase_900_D10.csv")
    itf.read_data("tensile/inl/AirBase_1000_D12.csv")

    # itf.read_data("creep/inl_1/AirBase_900_26_G59.csv")
    # itf.remove_oxidation()

    # itf.read_data("creep/inl_1/AirBase_1000_16_G18.csv")
    # itf.remove_oxidation()

    # itf.read_data("creep/inl_1/AirBase_1000_13_G30.csv")
    # itf.remove_oxidation(0.1, 0.7)

    # itf.read_data("creep/inl_1/AirBase_1000_12_G48.csv")
    # itf.remove_oxidation()

    # itf.read_data("creep/inl_1/AirBase_1000_11_G39.csv")
    # itf.remove_oxidation(0.1, 0.7)

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
    # itf.read_data("tensile/inl/AirBase_800_D7.csv")
    # itf.remove_manual("strain", 0.3)
    # itf.add_error("area", "strain", "stress")
    # itf.add_error("end", "strain")
    # itf.add_error("end", "stress")
    # itf.add_error("yield_point", yield_stress=291)
    
    # Apply driver
    # itf.set_custom_driver(
    #     driver_type = ls_tensile_driver,
    #     strain_rate = itf.get_data("strain_rate"),
    #     temperature = itf.get_data("temperature"),
    #     max_strain  = 1.0
    # )

    # Plot simulations
    # params_list = [10.691, 120.94, 82.538, 4.9475, 763.4, 1.7115, 5.9623, 143.1, 343.32, 29.234, 1.2529] # decent evpwdb 800
    # params_list = [10.691, 120.94, 82.538, 4.9475, 763.4]
    # itf.plot_simulation(params_list)

def truify_stress_strain(eng_stress, eng_strain):
    true_stress = eng_stress * (1 + eng_strain)
    true_strain = np.log(1 + eng_strain)
    return true_stress, true_strain

# Calls the main function
if __name__ == "__main__":
    main()
