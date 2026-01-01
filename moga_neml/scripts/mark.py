#!/usr/bin/env python3

import sys
sys.path.append('..')

from neml import solvers, models, elasticity, drivers, surfaces, hardening, ri_flow, visco_flow, general_flow, interpolate
from neml.nlsolvers import MaximumIterations, MaximumSubdivisions, newton, scalar_newton

import matplotlib.pyplot as plt
import numpy as np

def large_deformation_tension_driver(model, erate, T = 300.0, emax = 0.05,
                                     nsteps = 250, verbose = True,
                                     vorticity = np.zeros((3,))):
    strain = np.zeros((6,))

    strain_history = [strain]
    stress_history = [np.zeros((6,))]
    history_history = [model.init_store()]
    temperature_history = [T]
    time_history = [0.0]

    energy_history = [0.0]
    dissipation_history = [0.0]

    dt = emax / erate / nsteps
    einc = emax / nsteps

    for i in range(nsteps):
        temperature = T
        time = time_history[-1] + dt

        def advance(x):
            de = np.zeros((6,))
            de[0] = einc
            de[1:] = x

            return model.update_ld_inc(
                    strain_history[-1] + de, strain_history[-1], vorticity, vorticity,
                    temperature, temperature_history[-1], time, time_history[-1], stress_history[-1],
                    history_history[-1], energy_history[-1], dissipation_history[-1]) + (de,)

        def RJ(x):
            s_trial, _, A_trial, _, _, _, _ = advance(x)

            R = s_trial[1:]
            J = A_trial[1:,1:]

            return R, J
        
        x_guess = np.zeros((5,))
        x_guess[:2] = -0.5*einc

        x = newton(RJ, x_guess, verbose = False)

        stress, history, _, _, energy, dissipation, de = advance(x)
        
        strain_history.append(strain_history[-1] + de)
        stress_history.append(stress)
        history_history.append(history)
        temperature_history.append(temperature)
        time_history.append(time)
        energy_history.append(energy)
        dissipation_history.append(dissipation)


    strain_history = np.array(strain_history)
    stress_history = np.array(stress_history)

    return strain_history[:,0], stress_history[:,0]


if __name__ == "__main__":
    n = 20.0
    eta = 108.0
    sY = 89.0

    Q = 165.0
    b = 12.0

    C1 = 80.0e3
    C2 = 14.02e3
    C3 = 3.333e3

    y1 = 0.9e3
    y2 = 1.5e3
    y3 = 1.0

    surface = surfaces.IsoKinJ2()
    iso = hardening.VoceIsotropicHardeningRule(sY, Q, b)
    cs = [C1, C2, C3]
    gs = np.array([y1, y2, y3])
    gmodels = [hardening.ConstantGamma(g) for g in gs]
    hmodel = hardening.Chaboche(iso, cs, gmodels, [0.0] * len(cs),
      [1.0] * len(cs))

    fluidity = visco_flow.ConstantFluidity(eta)

    vmodel = visco_flow.ChabocheFlowRule(surface, hmodel, fluidity, n)

    E = 92000.0
    nu = 0.3

    mu = E/(2*(1+nu))
    K = E/(3*(1-2*nu))

    elastic = elasticity.IsotropicLinearElasticModel(mu, "shear", K, 
      "bulk")

    flow = general_flow.TVPFlowRule(elastic, vmodel)

    model = models.GeneralIntegrator(elastic, flow, verbose = False) 

    # Uniaxial tension 
    erate = 1.0e-4
    res = drivers.uniaxial_test(model, erate, emax = 0.5, nsteps = 500)
    plt.figure()
    plt.plot(res['strain'], res['stress'], label = "Small deformations")
    

    true_strain, true_stress = large_deformation_tension_driver(model, erate, emax = 0.5, nsteps = 500)
    plt.plot(true_strain, true_stress, label = "Large deformations")

    plt.xlabel("Strain (mm/mm)")
    plt.ylabel("Stress (MPa)")
    plt.title("Uniaxial tension")
    plt.legend(loc='best')
    plt.show()