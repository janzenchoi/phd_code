import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evpcd f 1000 st", input_path="../data", output_path="../results")

itf.define_model("evpcd")

params_str = """
0.004615	6.1843	2.2823	4.8326	460.27
3.9207	130.97	0.16188	3.9466	752.32
0.012675	18.528	0.99367	4.8134	471.18
0.26123	35.054	0.42681	4.7436	490.7
1.4714	3.11	5.9009	4.4241	584.77
4.1445	21.946	1.2583	3.9467	726.26
3.2085	17.287	1.3622	4.0769	697.16
4.3446	10.148	2.2066	3.8806	776.41
3.3748	51.076	0.45747	4.0575	700.49
4.2665	246.76	0.084953	3.9445	738.14
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]
itf.fix_params(params_list[int(sys.argv[1])])

itf.read_data("creep/inl_1/AirBase_1000_16_G18.csv")
itf.remove_oxidation()
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

itf.read_data("creep/inl_1/AirBase_1000_13_G30.csv")
itf.remove_oxidation(0.1, 0.7)
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

itf.read_data("creep/inl_1/AirBase_1000_12_G48.csv")
itf.remove_oxidation()

itf.read_data("creep/inl_1/AirBase_1000_11_G39.csv")
itf.remove_oxidation(0.1, 0.7)

itf.read_data("tensile/inl/AirBase_1000_D12.csv")
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=90)

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(10, plot_opt=True, plot_loss=True)
itf.optimise(10000, 100, 50, 0.8, 0.01)
