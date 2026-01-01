"""
 Title:         Large Strain
 Description:   For running customised large strain versions of existing NEML drivers
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from neml.nlsolvers import newton

# Driver Constants
NUM_STEPS    = 500
NUM_STEPS_UP = 200
MAX_STRAIN   = 1.0
CHECK_DAMAGE = False
# TIME_HOLD    = 15000.0 * 3600
# NUM_STEPS_UP = 50
DAMAGE_TOL   = 0.90 # 0.95
# STRESS_RATE  = 0.0001

# Solver constants
REL_TOL  = 1e-6
ABS_TOL  = 1e-10
MAX_ITER = 8
VERBOSE  = False
BT_TAU   = 0.5 # reduction factor
BT_C     = 1.0e-4 # criterion strictness

def ls_creep_driver(model, strain_rate:float, temperature:float, max_stress:float) -> dict:
    """
    A large strain creep driver

    Parameters:
    * `model`:       The NEML model object
    * `strain_rate`: The simulation strain rate
    * `temperature`: The simulation temperature
    * `max_stress`:  The maximum stress value
    
    Returns simulation results as a dictionary
    """

    # Initialise constants
    sd_index  = 0 # sample direction (xx)
    vorticity = np.zeros((3,))

    # Initialise histories
    time_list        = [0.0]
    strain_list      = [np.zeros((6,))]
    stress_list      = [np.zeros((6,))]
    history_list     = [model.init_store()]
    energy_list      = [0.0]
    dissipation_list = [0.0]

    # Ramp up
    stress_inc = float(max_stress) / NUM_STEPS_UP
    for step in range(NUM_STEPS_UP):
        pass

def ls_tensile_driver(model, strain_rate:float, temperature:float, max_strain:float=MAX_STRAIN) -> dict:
    """
    A large strain tensile driver

    Parameters:
    * `model`:       The NEML model object
    * `strain_rate`: The simulation strain rate
    * `temperature`: The simulation temperature
    * `max_strain`:  The maximum strain to evaluate
    
    Returns simulation results as a dictionary
    """

    # Initialise constants
    sd_index  = 0 # sample direction (xx)
    vorticity = np.zeros((3,))
    dt        = max_strain / strain_rate / NUM_STEPS
    e_inc     = max_strain / NUM_STEPS

    # Initialise histories
    strain_list      = [np.zeros((6,))]
    stress_list      = [np.zeros((6,))]
    history_list     = [model.init_store()]
    time_list        = [0.0]
    energy_list      = [0.0]
    dissipation_list = [0.0]
    
    # Prepare first initial guess
    x_guess = np.zeros((5,))
    x_guess[:2] = -0.3*e_inc

    # Iterate through steps
    for _ in range(NUM_STEPS):

        # Define large deformation incrementer
        def advance(x):
            de = np.concatenate(([e_inc], x))
            return model.update_ld_inc(strain_list[-1] + de, strain_list[-1], vorticity, vorticity,
                                       temperature, temperature, time_list[-1] + dt, time_list[-1],
                                       stress_list[-1], history_list[-1], energy_list[-1],
                                       dissipation_list[-1]) + (de,)
        
        # Define residual and jacobian for Newton method
        def get_rj(x):
            s_trial, _, A_trial, _, _, _, _ = advance(x)
            residual = s_trial[1:]
            jacobian = A_trial[1:,1:]
            return residual, jacobian
        
        # Apply large deformation
        try:
            x = newton(get_rj, x_guess, linesearch="backtracking", verbose=VERBOSE, rtol=REL_TOL, atol=ABS_TOL, miter=MAX_ITER, bt_tau=BT_TAU, bt_c=BT_C)
            # x = newton(get_rj, x_guess, verbose=VERBOSE, rtol=REL_TOL, atol=ABS_TOL, miter=MAX_ITER)
            stress, history, _, _, energy, dissipation, de = advance(x)
        except:
            break
        
        # Use current solution as next guess
        x_guess = x

        # Check damage
        damage = model.get_damage(history)
        if damage > DAMAGE_TOL:
            if CHECK_DAMAGE:
                raise Exception("Damage check exceeded")
            break

        # Append results to history
        strain_list.append(strain_list[-1] + de)
        stress_list.append(stress)
        history_list.append(history)
        time_list.append(time_list[-1] + dt)
        energy_list.append(energy)
        dissipation_list.append(dissipation)

    # Format and return simulation results
    sim_dict = {
        "time":    list(time_list),
        "strain":  [s[sd_index] for s in strain_list],
        "stress":  [s[sd_index] for s in stress_list],
        "history": list(history_list),
    }
    return sim_dict
