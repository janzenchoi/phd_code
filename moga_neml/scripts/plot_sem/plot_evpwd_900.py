import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
5.82	16.046	8.3648	4.1595	1064.7	38.773	222.24	393.28	859.75	2.3825	4.5047
11.616	16.725	6.3631	3.6491	1303.7	40.805	222.15	829.14	644.22	3.2018	1.2554
9.8394	12.026	14.017	3.7429	1275	36.916	211.85	498.46	952.62	2.4338	11.505
5.7368	8.3864	16.064	4.3916	855.39	33.396	191.41	420.91	779.17	3.6322	8.1479
7.5309	23.5	5.1998	3.862	1374.9	24.858	154.83	511.79	997.24	2.0041	7.9977
4.8239	389.25	0.18435	4.4133	941.87	44.974	248.15	621.83	913.9	2.4338	7.0609
6.6289	48.408	4.0515	3.7586	1383.6	45.15	253.49	553.63	866.98	1.6648	8.7312
16.262	181.79	0.52517	3.0161	2376.6	29.326	172.8	434.17	894.26	2.192	2.8518
6.3647	183.42	0.44712	4.1839	1075.3	27.326	165.15	422.54	849.67	2.2181	10.568
7.9872	16.104	7.2157	4.2939	892.7	13.577	93.551	360.21	764.12	1.9879	15.103

"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
itf.define_model("evpwdb")

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
# itf.remove_oxidation()
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
red_index = 8

# itf.plot_simulation(
#     params_list = params_list,
#     alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
#     limits_dict = {"creep": ((0, 7000), (0, 0.35)), "tensile": ((0, 1.0), (0, 250))},
# )

itf.plot_distribution(
    params_list = params_list,
    limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000),
                   "c_0": (0, 1000), "c_1": (0, 1000), "t_0": (0, 1000), "t_1": (0, 1000), "c_n": (0, 100), "t_n": (0, 100)},
    horizontal  = False
)
