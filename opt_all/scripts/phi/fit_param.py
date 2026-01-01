import sys; sys.path += ["../.."]
import numpy as np
from opt_all.interface import Interface

DATA_PATH = "../results/2025-10-05 phi_individual"

iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for _ in range(iters):

    for pn in ["phi_1", "phi_2", "phi_3", "phi_4"]:

        # Initialise model
        itf = Interface(f"phi_param_{pn}", input_path=DATA_PATH, output_path=DATA_PATH)
        # itf.define_model("phi/param", phi_param=pn)
        itf.define_model("phi/param_2", phi_param=pn)

        # Bind parameters
        # itf.bind_param("a", 0, 1e2)
        # itf.bind_param("n", 0, 1)
        # itf.bind_param("q", 0, 1e2)
        itf.bind_param("a", -1e3, 1e3)
        itf.bind_param("b", -1e3, 1e3)
        itf.bind_param("c", -1e3, 1e3)
        itf.bind_param("d", -1e3, 1e3)
        itf.bind_param("e", -1e3, 1e3)

        # Add calibration data
        itf.read_data("params_cal.csv")
        data_dict = itf.get_data()
        # itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])
        itf.add_error("area_1d", labels=[pn])

        # Add validation data
        itf.read_data("params_val.csv")
        data_dict = itf.get_data()
        # itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])

        # Set up recorder
        itf.start_recorder(interval=50000)
        itf.record_plot("stress", pn)

        # Optimise
        itf.optimise("moga", num_gens=1000, population=1000, offspring=1000, crossover=0.8, mutation=0.1)
