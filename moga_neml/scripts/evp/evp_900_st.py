import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evp 900 st t", input_path="../data", output_path="../results")

itf.define_model("evp")

itf.read_data("creep/inl_1/AirBase_900_36_G22.csv")
itf.remove_damage(0.1, 0.7)
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_900_31_G50.csv")
itf.remove_damage(0.1, 0.7)
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_900_28_G45.csv")
itf.remove_damage(0.2, 0.7)

itf.read_data("creep/inl_1/AirBase_900_26_G59.csv")
itf.remove_damage(0.1, 0.7)

itf.read_data("tensile/inl/AirBase_900_D10.csv")
itf.remove_manual("strain", 0.3)
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=164)

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(10, plot_opt=True, plot_loss=True)
itf.optimise(10000, 100, 50, 0.8, 0.01)
