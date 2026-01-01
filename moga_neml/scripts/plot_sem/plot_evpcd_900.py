import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
3.6262	13.804	6.9825	4.2416	1138.2	1986	4.4408	9.193
11.112	18.959	5.9505	3.6368	1471.6	2064.3	4.3164	7.225
11.394	13.887	7.532	3.5691	1581.2	1959.8	4.4121	8.5847
5.6656	7.6357	9.1337	4.3001	1055.4	3494.5	3.9629	11.623
8.0846	21.623	4.9985	3.8734	1330.8	2586.3	4.0925	6.8218
8.7008	379.67	0.15739	4.2166	994.53	1533.4	4.6802	7.0461
9.344	45.972	2.5375	3.4094	1902	2101.5	4.3022	6.1081
16.257	181.45	0.5026	3.0154	2606.2	2445.1	4.1307	5.6964
6.4694	149.62	0.29611	4.1942	1123.8	2045.9	4.4272	9.5323
7.9997	25.008	2.2597	4.127	1102.2	1841.7	4.5535	10.206

"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
itf.define_model("evpcd")

# itf.read_data("creep/inl_1/AirBase_900_36_G22.csv")
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_900_31_G50.csv")
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_900_28_G45.csv")
itf.read_data("creep/inl_1/AirBase_900_26_G59.csv")
itf.remove_oxidation()
itf.read_data("tensile/inl/AirBase_900_D10.csv")
itf.add_error("area", "strain", "stress")
# itf.add_error("yield_point", yield_stress=164)
# itf.add_error("max", "stress")
# itf.reduce_errors("square_average")
# itf.reduce_objectives("square_average")

# red_obj_list = []
# for params in params_list:
#     obj_dict = itf.__controller__.calculate_objectives(*params)
#     red_obj  = itf.__controller__.reduce_objectives(list(obj_dict.values()))
#     red_obj_list.append(red_obj)
# red_index = red_obj_list.index(min(red_obj_list))

red_index = 0

itf.plot_simulation(
    params_list = params_list,
    alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
    limits_dict = {"creep": ((0, 7000), (0, 0.35)), "tensile": ((0, 1.0), (0, 250))},
)

itf.plot_distribution(
    params_list = params_list,
    limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000),
                   "cd_A": (0, 10000), "cd_xi": (0, 100), "cd_phi": (0, 100)},
)
