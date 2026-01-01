import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
4.871	11.518	7.0281	4.2421	1138.3
11.208	16.738	5.9587	3.6377	1530.1
11.011	11.071	13.523	3.5672	1593.8
5.6656	8.2222	14.47	4.3001	1000.8
7.5292	23.505	4.9899	3.8623	1369.1
4.8238	378.86	0.1423	4.4021	1006.9
7.1037	48.235	4.2972	3.4084	1829.9
16.287	181.45	0.52517	3.0161	2606.2
6.3647	149.54	0.43913	4.1839	1127.6
7.044	16.175	6.7949	4.1207	1090
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
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
itf.remove_manual("strain", 0.328328866)
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=164)
itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

# red_obj_list = []
# for params in params_list:
#     obj_dict = itf.__controller__.calculate_objectives(*params)
#     red_obj  = itf.__controller__.reduce_objectives(list(obj_dict.values()))
#     red_obj_list.append(red_obj)
# red_index = red_obj_list.index(min(red_obj_list))

red_index = 8

itf.plot_simulation(
    params_list = params_list,
    alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
    clip        = True,
    limits_dict = {"creep": ((0, 7000), (0, 0.35)), "tensile": ((0, 1.0), (0, 250))},
)

# itf.plot_distribution(
#     params_list = params_list,
#     limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000)},
# )
