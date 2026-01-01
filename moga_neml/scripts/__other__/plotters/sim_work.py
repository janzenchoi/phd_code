import math, numpy as np
from scipy.interpolate import splev, splrep, splder
from copy import deepcopy
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow, damage, interpolate, drivers

# Constants
STRESS       = 80
TEMPERATURE  = 800
TIME_HOLD    = 15000.0 * 3600
NUM_STEPS    = 1300
VERBOSE      = False
NUM_STEPS_UP = 50
DAMAGE_TOL   = 0.95 # 0.95
STRESS_RATE  = 0.0001

def run(evp_s0, evp_R, evp_d, evp_n, evp_eta, wd_n, wd_0, wd_1, stress, temperature):
    
    # Define EVP model
    elastic_model = elasticity.IsotropicLinearElasticModel(157000, "youngs", 0.3, "poissons")
    yield_surface = surfaces.IsoJ2()
    iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
    g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
    visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
    integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
    evp_model     = models.GeneralIntegrator(elastic_model, integrator, verbose=False)
    
    # Prepare the critical points of the linear curve
    x_list = list(np.linspace(-12, 3, 32))
    y_list = [wd_0 * x + wd_1 for x in x_list]
    x_list = [math.pow(10, x) for x in x_list]
    wd_wc = interpolate.PiecewiseSemiLogXLinearInterpolate(x_list, y_list)
    
    # Run work damage model and return
    wd_model = damage.WorkDamage(elastic_model, wd_wc, wd_n, log=False, eps=1e-40, work_scale=1e5)
    evpwd_model = damage.NEMLScalarDamagedModel_sd(elastic_model, evp_model, wd_model, verbose=False)
    results = drivers.creep(evpwd_model, stress, STRESS_RATE, TIME_HOLD, T=temperature, verbose=VERBOSE,
                            check_dmg=True, dtol=DAMAGE_TOL, nsteps_up=NUM_STEPS_UP, nsteps=NUM_STEPS, logspace=False)
    for key in results.keys():
        if "time" in key:
            results[key] = [r/3600 for r in results[key]]
    return results

# Returns a thinned list
def get_thinned_list(unthinned_list:list, density:int) -> list:
    src_data_size = len(unthinned_list)
    step_size = src_data_size / density
    thin_indexes = [math.floor(step_size*i) for i in range(1, density - 1)]
    thin_indexes = [0] + thin_indexes + [src_data_size - 1]
    return [unthinned_list[i] for i in thin_indexes]

# The Interpolator Class
class Interpolator:

    # Constructor
    def __init__(self, x_list, y_list, resolution=50, smooth=False):
        x_list = get_thinned_list(x_list, resolution)
        y_list = get_thinned_list(y_list, resolution)
        smooth_amount = resolution if smooth else 0
        self.spl = splrep(x_list, y_list, s=smooth_amount)

    # Convert to derivative
    def differentiate(self):
        self.spl = splder(self.spl)

    # Evaluate
    def evaluate(self, x_list):
        return list(splev(x_list, self.spl))

# For differentiating a curve
def differentiate_curve(curve, x_label, y_label):
    curve = deepcopy(curve)
    interpolator = Interpolator(curve[x_label], curve[y_label])
    interpolator.differentiate()
    curve[y_label] = interpolator.evaluate(curve[x_label])
    return curve

params_str = """
17.217	179.74	0.61754	4.4166	1783.5	2.1462	24.063	167.25

"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]
stress_list = [80, 70, 65, 60]

import matplotlib.pyplot as plt

for params in params_list:
    for stress in stress_list:
        curve = run(*params, stress=stress, temperature=TEMPERATURE)
        d_curve = differentiate_curve(curve, "rtime", "rstrain")
        wc_list = [curve["rstrain"][i] * curve["stress"][i] for i in range(len(curve["rstrain"]))]
        wr_list = [d_curve["rstrain"][i] * curve["stress"][i] for i in range(len(d_curve["rstrain"]))]
        plt.plot(wr_list, wc_list, label=str(stress))
        # plt.plot(curve["time"], curve["strain"], color="red", label=str(stress))
        # plt.plot(curve["rtime"], curve["rstrain"], color="blue", label=str(stress))

plt.xscale("log")
plt.legend()
plt.savefig("plot.png")