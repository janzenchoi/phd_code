import sys; sys.path += ["../.."]
import numpy as np
from opt_all.interface import Interface

DATA_PATH = "theta"

iters = int(sys.argv[1]) if len(sys.argv) > 1 else 1
for _ in range(iters):

    for pn in ["t1", "t2", "t3", "t4"]:

        # Initialise model
        itf = Interface(f"theta_param_{pn}", input_path="../data", output_path="../results")
        itf.define_model("theta/param", theta_param=pn)

        # Bind parameters
        itf.bind_param("a", -1e2, 1e2)
        itf.bind_param("b", -2e2, 2e2)
        itf.bind_param("c", -1e2, 1e2)
        itf.bind_param("d", -2e2, 2e2)

        # Add calibration data
        itf.read_data(f"{DATA_PATH}/params_cal.csv")
        data_dict = itf.get_data()
        itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])
        itf.add_error("area_1d", labels=[pn])

        # Add validation data
        itf.read_data(f"{DATA_PATH}/params_val.csv")
        data_dict = itf.get_data()
        itf.change_data(pn, [pv*np.log(10) for pv in data_dict[pn]])

        # Set up recorder
        itf.start_recorder(interval=50000)
        itf.record_plot("stress", pn)

        # Optimise
        itf.optimise("moga", num_gens=1000, population=1000, offspring=1000, crossover=0.8, mutation=0.1)
