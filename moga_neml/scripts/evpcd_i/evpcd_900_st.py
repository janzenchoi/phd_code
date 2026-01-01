import sys; sys.path += ["../.."]
from moga_neml.interface import Interface

itf = Interface("evpcd i 900 st", input_path="../data", output_path="../results")

itf.define_model("evpcd")

params_str = """
4.871	11.518	7.0281	4.2421	1138.3	1899.3	4.4974	9.6201
11.208	16.738	5.9587	3.6377	1530.1	2070.2	4.3164	7.4964
11.011	11.071	13.523	3.5672	1593.8	1955.7	4.4015	8.5838
5.6656	8.2222	14.47	4.3001	1000.8	3494.5	3.9569	11.773
7.5292	23.505	4.9899	3.8623	1369.1	2070.7	4.3049	6.8212
4.8238	378.86	0.1423	4.4021	1006.9	1532	4.6818	6.5257
7.1037	48.235	4.2972	3.4084	1829.9	2105.1	4.188	3.5083
16.287	181.45	0.52517	3.0161	2606.2	2445.2	4.13	5.8583
6.3647	149.54	0.43913	4.1839	1127.6	1881.2	4.4539	6.9905
7.044	16.175	6.7949	4.1207	1090	1699.1	4.5578	8.0541
"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]
itf.init_params(params_list[int(sys.argv[1])])

itf.read_data("creep/inl_1/AirBase_900_36_G22.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

itf.read_data("creep/inl_1/AirBase_900_31_G50.csv")
itf.add_error("area", "time", "strain")
itf.add_error("end", "time")
itf.add_error("end", "strain")
itf.add_constraint("inc_end", "strain")
itf.add_constraint("dec_end", "time")

itf.read_data("creep/inl_1/AirBase_900_28_G45.csv")

itf.read_data("creep/inl_1/AirBase_900_26_G59.csv")
itf.remove_oxidation()

itf.read_data("tensile/inl/AirBase_900_D10.csv")
itf.add_error("area", "strain", "stress")
itf.add_error("yield_point", yield_stress=164)

itf.reduce_errors("square_average")
itf.reduce_objectives("square_average")

itf.plot_experimental()
itf.set_recorder(10, plot_opt=True, plot_loss=True)
itf.optimise(10000, 100, 50, 0.8, 0.01)
