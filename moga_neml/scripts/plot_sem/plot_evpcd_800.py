import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
16.994	187.83	0.26104	4.502	1784.8	3263.5	4.9231	13.172
22.454	66.77	0.92681	4.4191	1610.1	2142	5.4844	11.449
19.125	43.641	5.6148	4.1688	1616	1876.8	5.5594	6.8653
31.647	120.62	0.85485	3.7266	2297.8	2165.7	5.3247	7.7724
33.297	522.85	0.11871	3.9767	1762.4	1913.8	5.6638	11.287
15.042	35.437	8.4	3.9586	2283.5	4184.6	4.4257	6.6603
24.889	44.932	1.2076	4.5055	1527.9	2589.7	5.1066	8.695
23.304	276.66	0.32123	4.2592	1767.2	2168.5	5.3181	6.7619
30.401	34.817	4.5983	3.5323	2583	2520.9	5.1559	8.5891
5.0569	40.476	10.017	4.1585	1730.1	1998.1	5.5564	10.337
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
itf.define_model("evpcd")

# itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_800_65_G33.csv")
itf.read_data("creep/inl_1/AirBase_800_60_G32.csv")
itf.read_data("tensile/inl/AirBase_800_D7.csv")
itf.add_error("area", "strain", "stress")
# itf.add_error("yield_point", yield_stress=291)
# itf.add_error("max", "stress")
# itf.reduce_errors("square_average")
# itf.reduce_objectives("square_average")

# red_obj_list = []
# for params in params_list:
#     obj_dict = itf.__controller__.calculate_objectives(*params)
#     red_obj  = itf.__controller__.reduce_objectives(list(obj_dict.values()))
#     red_obj_list.append(red_obj)
# red_index = red_obj_list.index(min(red_obj_list))

red_index = 7

itf.plot_simulation(
    params_list = params_list,
    alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
    limits_dict = {"creep": ((0, 8000), (0, 0.7)), "tensile": ((0, 1.0), (0, 500))},
)

itf.plot_distribution(
    params_list = params_list,
    limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000),
                   "cd_A": (0, 10000), "cd_xi": (0, 100), "cd_phi": (0, 100)},
)
