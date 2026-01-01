import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evp 1000 st", input_path="../data", output_path="../results")

itf.define_model("evp")

itf.read_data("creep/inl_1/AirBase_1000_16_G18.csv")
itf.remove_manual("time", 900*3600)
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_1000_13_G30.csv")
itf.remove_manual("time", 1800*3600)
itf.add_error("area", "time", "strain")

itf.read_data("creep/inl_1/AirBase_1000_12_G48.csv")
itf.remove_manual("time", 2100*3600)

itf.read_data("creep/inl_1/AirBase_1000_11_G39.csv")
itf.remove_manual("time", 2500*3600)

itf.read_data("tensile/inl/AirBase_1000_D12.csv")
itf.remove_manual("strain", 0.3)
itf.add_error("yield_point", yield_stress=90)
itf.add_error("area", "strain", "stress")

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(10, plot_opt=True, plot_loss=True)
itf.optimise(10000, 100, 50, 0.8, 0.01)
