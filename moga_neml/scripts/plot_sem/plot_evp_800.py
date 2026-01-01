import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
17.217	179.74	0.61754	4.4166	1783.5
5.6908	66.627	1.9851	4.7723	1621.6
19.2	52.204	1.7579	4.5105	1614.6
31.327	104.92	0.8548	3.7508	2575.8
22.393	462.57	0.13573	4.314	1828.1
11.45	53.151	7.1666	3.9502	2221.6
18.768	89.18	0.88069	4.5055	1677.4
23.304	306.58	0.32123	4.2592	1822.6
31.137	31.413	4.6003	3.6958	2583
29.726	45.991	2.3174	3.9613	2101.3
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
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
itf.remove_manual("strain", 0.318238265)
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=291)
itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

# red_obj_list = []
# for params in params_list:
#     obj_dict = itf.__controller__.calculate_objectives(*params)
#     red_obj  = itf.__controller__.reduce_objectives(list(obj_dict.values()))
#     red_obj_list.append(red_obj)
# red_index = red_obj_list.index(min(red_obj_list))

red_index = 4

itf.plot_simulation(
    params_list = params_list,
    alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
    clip        = True,
    limits_dict = {"creep": ((0, 8000), (0, 0.7)), "tensile": ((0, 1.0), (0, 500))},
)

# itf.plot_distribution(
#     params_list = params_list,
#     limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000)},
# )
