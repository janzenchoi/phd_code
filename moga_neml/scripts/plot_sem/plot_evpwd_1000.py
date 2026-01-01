import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

params_str = """
0.13199	6.5191	11.588	4.5757	530.9	7.2545	51.111	244.85	554.46	1.4924	7.066
3.211	111.3	0.17971	4.0658	797.47	7.4637	50.736	283.99	637.4	1.4863	5.3119
0.013628	19.84	4.4536	4.4892	542.97	7.6866	53.311	281.25	622.97	1.3136	7.8413
0.2367	39.667	1.2775	4.4023	559.5	9.3449	62.201	262.65	587.44	2.0144	8.7398
1.3829	13.171	6.4312	4.1312	644.36	8.422	55.973	261.83	583.57	1.8614	11.981
3.455	16.732	6.9347	3.865	726.51	8.2554	55.102	253.49	563.13	1.3979	7.9624
2.7525	16.605	1.2867	4.2536	650.11	7.4409	51.438	248.11	562.08	1.554	8.8352
3.7022	24.227	2.4711	3.6321	870.39	8.2223	55.404	257.43	593.35	1.9805	8.9843
2.7156	41.193	0.31274	4.0819	825.7	10.001	64.808	248.52	559.21	1.6577	10.642
3.32	381.2	0.07715	4.1319	716.42	7.8478	53.547	261.99	583.71	1.3314	8.2668

"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

itf = Interface("plot", output_here=True, input_path="../data", output_path="../results")
itf.define_model("evpwdb")

# itf.read_data("creep/inl_1/AirBase_1000_16_G18.csv")
# itf.remove_oxidation()
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_1000_13_G30.csv")
# itf.remove_oxidation(0.1, 0.7)
# itf.add_error("area", "time", "strain")
# itf.add_error("end", "time")
# itf.add_error("end", "strain")
# itf.add_constraint("inc_end", "strain")
# itf.add_constraint("dec_end", "time")
# itf.read_data("creep/inl_1/AirBase_1000_12_G48.csv")
# itf.remove_oxidation()
itf.read_data("creep/inl_1/AirBase_1000_11_G39.csv")
itf.remove_oxidation(0.1, 0.7)
itf.read_data("tensile/inl/AirBase_1000_D12.csv")
itf.add_error("area", "strain", "stress")
# itf.add_error("yield_point", yield_stress=90)
# itf.add_error("max", "stress")
# itf.reduce_errors("square_average")
# itf.reduce_objectives("square_average")

# red_obj_list = []
# for params in params_list:
#     obj_dict = itf.__controller__.calculate_objectives(*params)
#     red_obj  = itf.__controller__.reduce_objectives(list(obj_dict.values()))
#     red_obj_list.append(red_obj)
# red_index = red_obj_list.index(min(red_obj_list))

red_index = 3

itf.plot_simulation(
    params_list = params_list,
    alpha_list  = [0.2 if i != red_index else 1.0 for i in range(len(params_list))],
    limits_dict = {"creep": ((0, 8000), (0, 0.35)), "tensile": ((0, 1.0), (0, 160))},
)

itf.plot_distribution(
    params_list = params_list,
    limits_dict = {"evp_s0": (0, 100), "evp_R": (0, 1000), "evp_d": (0, 100), "evp_n": (0, 100), "evp_eta": (0, 10000),
                   "c_0": (0, 1000), "c_1": (0, 1000), "t_0": (0, 1000), "t_1": (0, 1000), "c_n": (0, 100), "t_n": (0, 100)},
)
