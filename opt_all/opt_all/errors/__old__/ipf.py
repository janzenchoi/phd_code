"""
 Title:         The ipf objective function
 Description:   The objective function for minimising the positions on the ipf plot
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from neml.math import rotations, tensors
from neml.cp import crystallography
from opt_all.errors.__error__ import __Error__

# The IPF class
class Error(__Error__):
    
    def initialise(self, structure:str="bcc", direction:list=[0,1,0]):
        """
        Runs at the start, once

        * `strain`:    The strain to evaluate
        * `structure`: The lattice ("bcc", "fcc")
        * `direction`: The direction of the IPF
        """

        # Initialise lattice and direction
        self.lattice = crystallography.CubicLattice(1.0)
        if structure == "fcc":
            self.lattice.add_slip_system([1,1,0], [1,1,1])
        elif structure == "bcc":
            self.lattice.add_slip_system([1,1,1], [1,1,0])
            self.lattice.add_slip_system([1,1,1], [1,2,3])
            self.lattice.add_slip_system([1,1,1], [1,1,2])
        self.direction = direction

        # Initialise euler angles
        exp_data = self.get_exp_data()
        self.labels = self.get_labels()[0:]
        init_euler = [exp_data[label][0] for label in self.labels]
        exp_euler = [exp_data[label][-1] for label in self.labels]

        # Get IPF points
        self.init_ipf = get_points(init_euler, self.direction, self.lattice)[-1]
        exp_ipf = get_points(exp_euler, self.direction, self.lattice)[-1]
        self.exp_grad = (exp_ipf[1] - self.init_ipf[1])/(exp_ipf[0] - self.init_ipf[0])

    def get_value(self, prd_data:dict) -> float:
        """
        Computing the NRMSE

        Parameters:
        * `prd_data`: The predicted data

        Returns the error
        """
        prd_euler = [prd_data[label][-1] for label in self.labels]
        prd_ipf = get_points(prd_euler, self.direction, self.lattice)[-1]
        prd_grad = (prd_ipf[1] - self.init_ipf[1])/(prd_ipf[0] - self.init_ipf[0])
        return abs((self.exp_grad-prd_grad)/self.exp_grad)

def get_points(euler:list, direction:list, lattice) -> list:
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
    stereo_points  = np.array([project_stereographic(point) for point in reduced_points])
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
