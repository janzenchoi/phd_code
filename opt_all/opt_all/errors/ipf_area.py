"""
 Title:         The ipf area objective function
 Description:   The objective function for minimising the vertical areas between two sets
                of orientations on an IPF plot
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from neml.math import rotations, tensors
from neml.cp import crystallography
from opt_all.errors.__error__ import __Error__
from opt_all.helper.interpolator import Interpolator
from opt_all.helper.general import transpose

# The IPF Area class
class Error(__Error__):
    
    def initialise(self, structure:str="fcc", direction:list=[1,0,0]):
        """
        Runs at the start, once

        * `structure`:  The lattice ("bcc", "fcc")
        * `direction`:  The direction of the IPF
        """

        # Initialise material information
        direction = direction
        lattice = get_lattice(structure)
        self.get_ipf_point = lambda euler : get_ipf_point(euler, direction, lattice)

        # Get experimental data
        exp_strain_list = self.get_data("strain_intervals")
        exp_trajectory  = [self.get_data(label) for label in self.get_labels()]
        exp_trajectory  = transpose(exp_trajectory)
        
        # Prepare experimental IPF
        exp_ipf = transpose([self.get_ipf_point(euler)[0] for euler in exp_trajectory])
        self.exp_x_itp = Interpolator(exp_strain_list, exp_ipf[0], len(exp_strain_list))
        self.exp_y_itp = Interpolator(exp_strain_list, exp_ipf[1], len(exp_strain_list))
        self.exp_avg_x = np.average(exp_ipf[0])
        self.exp_avg_y = np.average(exp_ipf[1])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """

        # Get predicted data
        max_prd_strain = max(prd_data["strain"])
        prd_strain_list = [pct*max_prd_strain for pct in [0, 0.2, 0.4, 0.6, 0.8, 1.0]]
        prd_trajectory = [prd_data[label] for label in self.get_labels()]
        prd_trajectory  = transpose(prd_trajectory)
        prd_ipf = transpose([self.get_ipf_point(euler)[0] for euler in prd_trajectory])

        # Get experimental IPF
        exp_x_list = self.exp_x_itp.evaluate(prd_strain_list)
        exp_y_list = self.exp_y_itp.evaluate(prd_strain_list)

        # Calculate areas
        area_x = [abs(exp_x-prd_x) for exp_x, prd_x in zip(exp_x_list, prd_ipf[0])]
        area_y = [abs(exp_y-prd_y) for exp_y, prd_y in zip(exp_y_list, prd_ipf[1])]
        error_x = np.average(area_x)/self.exp_avg_x
        error_y = np.average(area_y)/self.exp_avg_y
        return np.average([error_x, error_y])

def get_lattice(structure:str="fcc") -> crystallography.Lattice:
    """
    Gets the lattice object

    Parameters:
    * `structure`: The crystal structure

    Returns the lattice object
    """
    lattice = crystallography.CubicLattice(1.0)
    if structure == "fcc":
        lattice.add_slip_system([1,1,0], [1,1,1])
    elif structure == "bcc":
        lattice.add_slip_system([1,1,1], [1,1,0])
        lattice.add_slip_system([1,1,1], [1,2,3])
        lattice.add_slip_system([1,1,1], [1,1,2])
    else:
        raise ValueError(f"Crystal structure '{structure}' unsupported!")
    return lattice

def get_ipf_point(euler:list, direction:list, lattice) -> list:
    """
    Converts an euler orientation into stereo points

    Parameters:
    * `euler`:     The orientation in euler-bunge form (rads)
    * `direction`: Direction of the projection
    * `lattice`:   Lattice of crystals

    Returns a list of stereo points
    """
    orientation = rotations.CrystalOrientation(euler[0], euler[1], euler[2], angle_type="radians", convention="bunge")
    projected_points = project_ipf(orientation, direction, lattice)
    projected_points = np.vstack(tuple(projected_points))
    reduced_points = reduce_points_triangle(projected_points)
    stereo_points  = [project_stereographic(point) for point in reduced_points]
    stereo_points  = [list(sp) for sp in stereo_points]
    return stereo_points

def project_ipf(quaternion:np.array, direction:list, lattice) -> None:
    """
    Projects a single sample direction onto a crystal

    Parameters:
    * `quaternion`: Orientation in quaternion form
    * `direction`:  Direction of the projection
    * `lattice`:    Lattice of crystals

    Returns the projected points
    """

    # Normalise lattice directions
    norm_x  = lattice.miller2cart_direction([1,0,0]).normalize()
    norm_y  = lattice.miller2cart_direction([0,1,0]).normalize()
    if not np.isclose(norm_x.dot(norm_y), 0.0):
        raise ValueError("Lattice directions are not orthogonal!")
    norm_z = norm_x.cross(norm_y)
    trans  = rotations.Orientation(np.vstack((norm_x.data, norm_y.data, norm_z.data)))
    norm_d = tensors.Vector(np.array(direction)).normalize()

    # Populate the points
    points_list = []
    sample_symmetry = crystallography.symmetry_rotations("222")
    for rotation in sample_symmetry:
        sample_points = rotation.apply(norm_d)
        crystal_points = quaternion.apply(sample_points)
        points = [trans.apply(op.apply(crystal_points)).data for op in lattice.symmetry.ops]
        points_list += points

    # Format the points in the upper hemisphere and return
    points_list = np.array(points_list)
    points_list = points_list[points_list[:,2] > 0]
    return points_list

def project_stereographic(vector:np.array) -> np.array:
    """
    Stereographic projection of the given vector into a numpy array

    Parameters:
    * `vector`: Unprojected vector
    
    Returns the projected vector
    """
    return np.array([vector[0]/(1.0+vector[2]), vector[1]/(1.0+vector[2])])

def reduce_points_triangle(points:tuple) -> list:
    """
    Reduce points to a standard stereographic triangle

    Parameters:
    * `points`: The projected points
    
    Returns the reduced points
    """
    vectors = (np.array([0,0,1.0]), np.array([1.0,0,1]), np.array([1.0,1,1])) # force float
    norm_vectors = [vector / np.linalg.norm(np.array(vector)) for vector in vectors]
    norm_0 = np.cross(norm_vectors[0], norm_vectors[1])
    norm_1 = np.cross(norm_vectors[1], norm_vectors[2])
    norm_2 = np.cross(norm_vectors[2], norm_vectors[0])
    reduced_points = [p for p in points if np.dot(p, norm_0) >= 0 and np.dot(p, norm_1) >= 0 and np.dot(p, norm_2) >= 0]
    return reduced_points
