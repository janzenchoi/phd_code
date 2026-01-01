"""
 Title:         The Elastic Viscoplastic Work Damage Model with bilinear function for work damage
 Description:   Incorporates elasto-viscoplasticity and work damage
 Author:        Janzen Choi

"""

# Libraries
import numpy as np, math
from moga_neml.io.plotter import Plotter
from moga_neml.models.__model__ import __Model__
from neml import models, elasticity, surfaces, hardening, visco_flow, general_flow, damage, interpolate

# Constants
TAIL_LENGTH = 5
RESOLUTION  = 32
MAX_WORK    = 5 # power of 10

# The Elastic Visco Plastic Work Damage Class
class Model(__Model__):

    def initialise(self):
        """
        Runs at the start, once
        """

        # Elastic parameters
        self.add_param("evp_s0",  0.0e0, 1.0e2) # 3 (</ 1e2)
        self.add_param("evp_R",   0.0e0, 1.0e3) # 4
        self.add_param("evp_d",   0.0e0, 1.0e2) # 2
        self.add_param("evp_n",   0.0e0, 1.0e2) # 2
        self.add_param("evp_eta", 0.0e0, 1.0e4) # 5
        
        # Critical work parameters
        self.add_param("c_0", 0e0, 1.0e3)
        self.add_param("c_1", 0e0, 1.0e3)
        self.add_param("t_0", 0e0, 1.0e3)
        self.add_param("t_1", 0e0, 1.0e3)

        # Exponent parameters
        self.add_param("c_n", 0.0e0, 1.0e2)
        self.add_param("t_n", 0.0e0, 1.0e2)

    def calibrate_model(self, evp_s0:float, evp_R:float, evp_d:float, evp_n:float, evp_eta:float,
                        c_0:float, c_1:float, t_0:float, t_1:float, c_n:float, t_n:float):
        """
        Gets the predicted curves

        Parameters:
        * `evp_s0`:  Initial yield stress
        * `evp_R`:   Isotropic hardening stress
        * `evp_d`:   Isotropic hardening rate
        * `evp_n`:   Rate sensitivity
        * `evp_eta`: Viscoplastic fluidity
        * `c_0`:     Gradient for left side of bilinear function
        * `c_1`:     Vertical intercept for left side of bilinear function
        * `t_0`:     Gradient for right side of bilinear function
        * `t_1`:     Vertical intercept for right side of bilinear function
        * `c_n`:     The exponent value for the left side of bilinear function
        * `t_n`:     The exponent value for the right side of bilinear function

        Returns the calibrated model
        """

        # If tensile shelf is not higher than creep shelf, then bad parameters
        if t_0 < c_0 or t_1 < c_1:
            return

        # Define EVP model
        elastic_model = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                               self.get_data("poissons"), "poissons")
        yield_surface = surfaces.IsoJ2()
        iso_hardening = hardening.VoceIsotropicHardeningRule(evp_s0, evp_R, evp_d)
        g_power       = visco_flow.GPowerLaw(evp_n, evp_eta)
        visco_model   = visco_flow.PerzynaFlowRule(yield_surface, iso_hardening, g_power)
        integrator    = general_flow.TVPFlowRule(elastic_model, visco_model)
        evp_model     = models.GeneralIntegrator(elastic_model, integrator, verbose=False)
        
        # Gets the interpolators
        wr_wc_list, wc_list = get_wc_data(c_0, c_1, t_0, t_1)
        wr_n_list, n_list = get_n_data(c_0, c_1, t_0, t_1, c_n, t_n)
        wd_wc = interpolate.PiecewiseSemiLogXLinearInterpolate(wr_wc_list, wc_list)
        wd_n = interpolate.PiecewiseSemiLogXLinearInterpolate(wr_n_list, n_list)
        
        # Define work damage model and return
        wd_model = damage.WorkDamage(elastic_model, wd_wc, wd_n, log=False, eps=1e-40, work_scale=1e5)
        evpwd_model = damage.NEMLScalarDamagedModel_sd(elastic_model, evp_model, wd_model, verbose=False)
        return evpwd_model

    def record_results(self, output_path:str, evp_s0:float, evp_R:float, evp_d:float, evp_n:float, evp_eta:float,
                        c_0:float, c_1:float, t_0:float, t_1:float, c_n:float, t_n:float) -> None:
        """
        Records the interpolators

        Parameters:
        * `output_path`: The path to the output directory
        * `evp_s0`:      Initial yield stress
        * `evp_R`:       Isotropic hardening stress
        * `evp_d`:       Isotropic hardening rate
        * `evp_n`:       Rate sensitivity
        * `evp_eta`:     Viscoplastic fluidity
        * `c_0`:         Gradient for left side of bilinear function
        * `c_1`:         Vertical intercept for left side of bilinear function
        * `t_0`:         Gradient for right side of bilinear function
        * `t_1`:         Vertical intercept for right side of bilinear function
        * `c_n`:         The exponent value for the left side of bilinear function
        * `t_n`:         The exponent value for the right side of bilinear function

        Returns the calibrated model
        """

        # Plot wr-wc
        wr_wc_list, wc_list = get_wc_data(c_0, c_1, t_0, t_1)
        wc_plotter = Plotter(f"{output_path}/critical_work.png", "Work Rate", "Critical Work")
        wc_plotter.prep_plot()
        wc_plotter.scat_plot({"Work Rate": wr_wc_list, "Critical Work": wc_list})
        wc_plotter.set_log_scale(x_log=True)
        wc_plotter.save_plot()
        wc_plotter.clear()

        # Plot wr-wc
        wr_n_list, n_list = get_n_data(c_0, c_1, t_0, t_1, c_n, t_n)
        wc_plotter = Plotter(f"{output_path}/damage_exponent.png", "Work Rate", "Damage Exponent")
        wc_plotter.prep_plot()
        wc_plotter.scat_plot({"Work Rate": wr_n_list, "Damage Exponent": n_list})
        wc_plotter.set_log_scale(x_log=True)
        wc_plotter.save_plot()
        wc_plotter.clear()

def get_bounds(c_0:float, c_1:float, t_0:float, t_1:float) -> tuple:
    """
    Gets the interpolation bilinear points
    
    Parameters:
    * `c_0`: Gradient for left side of bilinear function
    * `c_1`: Vertical intercept for left side of bilinear function
    * `t_0`: Gradient for right side of bilinear function
    * `t_1`: Vertical intercept for right side of bilinear function
    
    Returns the intervals of the interpolation
    """
    wr_0 = -c_1/c_0
    wr_1 = (t_1-c_1) / (c_0-t_0)
    wr_2 = MAX_WORK
    return wr_0, wr_1, wr_2

def get_wc(wr:float, c_0:float, c_1:float, t_0:float, t_1:float) -> float:
    """
    Gets the critical work
    
    Parameters:
    * `wr`:  The work rate value
    * `c_0`: Gradient for left side of bilinear function
    * `c_1`: Vertical intercept for left side of bilinear function
    * `t_0`: Gradient for right side of bilinear function
    * `t_1`: Vertical intercept for right side of bilinear function
    
    Returns the critical work
    """
    wr_0, wr_1, _ = get_bounds(c_0, c_1, t_0, t_1)
    if wr <= wr_0 + 1:
        return c_0 * math.exp(wr - wr_0 - 1)
    elif wr <= wr_1:
        return c_0*wr + c_1
    else:
        return t_0*wr + t_1

def get_wc_data(c_0:float, c_1:float, t_0:float, t_1:float) -> tuple:
    """
    Gets the work rate and critical work values
    
    Parameters:
    * `c_0`: Gradient for left side of bilinear function
    * `c_1`: Vertical intercept for left side of bilinear function
    * `t_0`: Gradient for right side of bilinear function
    * `t_1`: Vertical intercept for right side of bilinear function
    
    Returns lists of work rate and critical work values
    """
    wr_0, wr_1, wr_2 = get_bounds(c_0, c_1, t_0, t_1)
    wr_list = list(np.linspace(wr_0-TAIL_LENGTH, wr_0+1, RESOLUTION)) +\
              list(np.linspace(wr_0+1, wr_1, RESOLUTION)) +\
              list(np.linspace(wr_1, wr_2, RESOLUTION))
    wc_list = [get_wc(wr, c_0, c_1, t_0, t_1) for wr in wr_list]
    wr_list = [math.pow(10, wr) for wr in wr_list]
    return wr_list, wc_list

def get_n(wr:float, c_0:float, c_1:float, t_0:float, t_1:float, c_n:float, t_n:float) -> tuple:
    """
    Gets the exponent value from the work rate
    
    Parameters:
    * `wr`: The work rate value
    * `c_0`: Gradient for left side of bilinear function
    * `c_1`: Vertical intercept for left side of bilinear function
    * `t_0`: Gradient for right side of bilinear function
    * `t_1`: Vertical intercept for right side of bilinear function
    * `c_n`: The exponent value for the left side of bilinear function
    * `t_n`: The exponent value for the right side of bilinear function
    
    Returns the exponent value
    """
    _, wr_1, _ = get_bounds(c_0, c_1, t_0, t_1)
    if wr <= wr_1-0.5:
        return c_n
    elif wr_1-0.5 < wr and wr <= wr_1+0.5:
        return (t_n-c_n)/2*math.sin(math.pi*(wr - wr_1)) + (t_n+c_n)/2
    else:
        return t_n

def get_n_data(c_0:float, c_1:float, t_0:float, t_1:float, c_n:float, t_n:float) -> tuple:
    """
    Gets the work rate and exponent values
    
    Parameters:
    * `c_0`: Gradient for left side of bilinear function
    * `c_1`: Vertical intercept for left side of bilinear function
    * `t_0`: Gradient for right side of bilinear function
    * `t_1`: Vertical intercept for right side of bilinear function
    * `c_n`: The exponent value for the left side of bilinear function
    * `t_n`: The exponent value for the right side of bilinear function
    
    Returns lists of work rate and exponent values
    """
    wr_0, wr_1, wr_2 = get_bounds(c_0, c_1, t_0, t_1)
    wr_list = list(np.linspace(wr_0-TAIL_LENGTH, wr_1-0.5, RESOLUTION)) +\
              list(np.linspace(wr_1-0.5, wr_1+0.5, RESOLUTION)) +\
              list(np.linspace(wr_1+0.5, wr_2, RESOLUTION))
    n_list = [get_n(wr, c_0, c_1, t_0, t_1, c_n, t_n) for wr in wr_list]
    wr_list = [math.pow(10, wr) for wr in wr_list]
    return wr_list, n_list
