"""
 Title:         The Voce Slip Hardening Asaro Inelasticity Model
 Description:   Incorporates crystal plasticity
 Author:        Janzen Choi

"""

# Libraries
from neml import elasticity
from neml.cp import crystallography, slipharden, sliprules, inelasticity, kinematics, singlecrystal, polycrystal
from neml.math import rotations
from moga_neml.models.__model__ import __Model__

# The Voce Slip Hardening Asaro Inelasticity Class
class Model(__Model__):

    # itf.define_model("vshai", ori_path="data/ebsd/input_stats.csv", lattice=1.0, slip_dir=[1,1,0], slip_plane=[1,1,1], num_threads=16)
    def initialise(self, ori_path:str, lattice:float, slip_dir:list, slip_plane:list, num_threads:int):
        """
        Runs at the start, once
        """

        # Defines the parameters
        self.add_param("vsh_ts", 0.0e0, 2.0e3)
        self.add_param("vsh_b",  0.0e0, 1.0e1)
        self.add_param("vsh_t0", 0.0e0, 1.0e3)
        self.add_param("ai_g0",  0.0e0, 1.0e0)
        self.add_param("ai_n",   0.0e0, 1.0e2)
    
        # Extract information from arguments
        self.num_threads = num_threads

        # Define grain orientations
        file = open(f"{ori_path}", "r")
        self.grain_orientations, self.weights = [], []
        for line in file.readlines():
            data = line.replace("\n","").split(",")
            phi_1 = float(data[0])
            Phi   = float(data[1])
            phi_2 = float(data[2])
            if phi_1 == 0 and Phi == 0 and phi_2 == 0:
                continue
            self.grain_orientations.append(rotations.CrystalOrientation(phi_1, Phi, phi_2,
                                           angle_type="degrees", convention="bunge"))
            self.weights.append(int(data[3]))
        file.close()

        # Define lattice structure
        self.lattice = crystallography.CubicLattice(lattice)
        self.lattice.add_slip_system(slip_dir, slip_plane)
        
    def calibrate_model(self, vsh_ts, vsh_b, vsh_t0, ai_g0, ai_n):
        """
        Gets the predicted curves

        Parameters:
        * `...`: ...

        Returns the calibrated model
        """
        elastic_model  = elasticity.IsotropicLinearElasticModel(self.get_data("youngs"), "youngs",
                                                                self.get_data("poissons"), "poissons")
        strength_model = slipharden.VoceSlipHardening(vsh_ts, vsh_b, vsh_t0)
        slip_model     = sliprules.PowerLawSlipRule(strength_model, ai_g0, ai_n)
        ai_model       = inelasticity.AsaroInelasticity(slip_model)
        ep_model       = kinematics.StandardKinematicModel(elastic_model, ai_model)
        sc_model       = singlecrystal.SingleCrystalModel(ep_model, self.lattice, verbose=False, miter=16, max_divide=2)
        vshai_model    = polycrystal.TaylorModel(sc_model, self.grain_orientations, nthreads=self.num_threads, weights=self.weights)
        return vshai_model
