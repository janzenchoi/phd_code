"""
 Title:         Driver
 Description:   For running the NEML drivers
 Author:        Janzen Choi

"""

# Libraries
from neml import drivers
from moga_neml.helper.experiment import NEML_FIELD_CONVERSION
from moga_neml.helper.general import BlockPrint
from moga_neml.helper.data import find_tensile_strain_to_failure, remove_data_after
from moga_neml.optimise.curve import Curve

# General Driver Constants
TIME_HOLD    = 15000.0 * 3600
NUM_STEPS    = 1300
REL_TOL      = 1e-6
ABS_TOL      = 1e-10
MAX_STRAIN   = 1.0
VERBOSE      = False
NUM_STEPS_UP = 50
DAMAGE_TOL   = 0.95
STRESS_RATE  = 0.0001
CYCLIC_RATIO = -1

# Driver class
class Driver:
    
    def __init__(self, curve:Curve, calibrated_model) -> None:
        """
        Initialises the driver class
        
        Parameters:
        * `curve`:      The curve the driver is being used on
        * `model`:      The calibrated model to be run
        """
        self.curve     = curve
        self.exp_data  = curve.get_exp_data()
        self.type      = self.exp_data["type"]
        self.conv_dict = NEML_FIELD_CONVERSION[self.type]
        self.calibrated_model = calibrated_model
    
    def run(self) -> dict:
        """
        Runs the driver based on the experimental curve type;
        returns the results
        """

        # Get the results
        results = self.run_selected()
        # try:
        #     with BlockPrint():
        #         results = self.run_selected()
        # except:
        #     return
        
        # Convert results and return
        converted_results = {}
        for field in list(self.conv_dict.keys()):
            if field in results.keys():
                converted_results[self.conv_dict[field]] = list(results[field])
        if self.type == "tensile":
            end_index = find_tensile_strain_to_failure(converted_results["stress"])
            if end_index != None:
                end_strain = converted_results["strain"][end_index]
                converted_results = remove_data_after(converted_results, end_strain, "strain")
        return converted_results
    
    def run_selected(self) -> dict:
        """
        Runs the driver depending on the data type;
        returns the results
        """

        # Runs custom driver if it is defined
        custom_driver, custom_driver_kwargs = self.curve.get_custom_driver()
        if custom_driver != None:
            if isinstance(custom_driver, str):
                custom_driver = getattr(drivers, custom_driver)
            results = custom_driver(self.calibrated_model, **custom_driver_kwargs)
            return results

        # Runs driver based on data type
        if self.type == "creep":
            return self.run_creep()
        elif self.type == "tensile":
            return self.run_tensile()
        elif self.type == "cyclic":
            return self.run_cyclic()
        raise ValueError(f"The data type '{self.type}' is not supported; use the 'custom_driver' function to define a custom driver")

    def run_creep(self) -> dict:
        """
        Runs the creep driver;
        returns the results
        """
        results = drivers.creep(self.calibrated_model, self.exp_data["stress"], STRESS_RATE, TIME_HOLD,
                                T=self.exp_data["temperature"], verbose=VERBOSE, check_dmg=True,
                                dtol=DAMAGE_TOL, nsteps_up=NUM_STEPS_UP, nsteps=NUM_STEPS, logspace=False)
        return results

    def run_tensile(self) -> dict:
        """
        Runs the tensile driver;
        returns the results
        """
        results = drivers.uniaxial_test(self.calibrated_model, erate=self.exp_data["strain_rate"], T=self.exp_data["temperature"],
                                        emax=MAX_STRAIN, check_dmg=True, dtol=DAMAGE_TOL, nsteps=NUM_STEPS,
                                        verbose=VERBOSE, rtol=REL_TOL, atol=ABS_TOL)
        return results
    
    def run_cyclic(self) -> dict:
        """
        Runs the cyclic driver;
        returns the results
        """
        num_cycles = int(self.exp_data["num_cycles"])
        results = drivers.strain_cyclic(self.calibrated_model, T=self.exp_data["temperature"], emax=self.exp_data["max_strain"],
                                        erate=self.exp_data["strain_rate"], verbose=VERBOSE, R=CYCLIC_RATIO,
                                        ncycles=num_cycles, nsteps=NUM_STEPS)
        return results
