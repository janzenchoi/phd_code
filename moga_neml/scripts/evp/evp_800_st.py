import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evp 800 st t", input_path="../data", output_path="../results")

itf.define_model("evp")

itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.remove_damage()
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.remove_damage()
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_800_65_G33.csv")
itf.remove_damage(0.1, 0.7)

itf.read_data("creep/inl_1/AirBase_800_60_G32.csv")
itf.remove_damage(0.1, 0.7)

itf.read_data("tensile/inl/AirBase_800_D7.csv")
itf.remove_manual("strain", 0.3)
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=291)

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(10, plot_opt=True, plot_loss=True)
itf.optimise(10000, 100, 50, 0.8, 0.01)
