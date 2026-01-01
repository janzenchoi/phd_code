import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evpwdb i 800 st", input_path="../data", output_path="../results")

itf.define_model("evpwdb")

params_str = """
17.217	179.74	0.61754	4.4166	1783.5	46.898	316.15	215.23	965.64	1.3295	0.79851
5.6908	66.627	1.9851	4.7723	1621.6	40.432	261.28	111.09	652.01	2.6708	1.0401
19.2	52.204	1.7579	4.5105	1614.6	40.854	277.59	369.86	791.5	1.6558	8.0179
31.327	104.92	0.8548	3.7508	2575.8	42.29	268.44	130.88	530.45	2.0456	0.9014
22.393	462.57	0.13573	4.314	1828.1	16.398	130.12	159.23	767.17	2.091	0.85695
11.45	53.151	7.1666	3.9502	2221.6	53.588	359.25	136.66	490.18	1.1624	7.2208
18.768	89.18	0.88069	4.5055	1677.4	34.704	234.31	152.15	436.05	1.9003	19.809
23.304	306.58	0.32123	4.2592	1822.6	52.929	322.05	399.31	903.55	1.9698	18.199
31.137	31.413	4.6003	3.6958	2583	66.391	394.7	263.33	475.75	1.928	10.99
29.726	45.991	2.3174	3.9613	2101.3	18.24	140.86	104.34	534.77	1.9632	1.6899
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]
itf.init_params(params_list[int(sys.argv[1])])

itf.read_data("creep/inl_1/AirBase_800_80_G25.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

itf.read_data("creep/inl_1/AirBase_800_70_G44.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")

itf.read_data("creep/inl_1/AirBase_800_65_G33.csv")

itf.read_data("creep/inl_1/AirBase_800_60_G32.csv")

itf.read_data("tensile/inl/AirBase_800_D7.csv")
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=291)

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(1, plot_opt=True, plot_loss=True)
itf.optimise(500, 100, 50, 0.8, 0.01)
