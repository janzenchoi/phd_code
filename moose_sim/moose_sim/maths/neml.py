"""
 Title:         NEML
 Description:   Helper functions that use NEML
 Author:        Janzen Choi

"""

# Libraries
import math
from moose_sim.maths.orientation import fix_angle
from neml.math import rotations
from neml.cp import crystallography

def get_cubic_misorientation(euler_1:list, euler_2:list):
    """
    Determines the misorientation of two sets of euler angles (rads);
    assumes cubic structure

    Parameters:
    * `euler_1`: The first euler angle
    * `euler_2`: The second euler angle
    
    Returns the misorientation angle
    """
    euler_1 = rotations.CrystalOrientation(*euler_1, angle_type="radians", convention="bunge")
    euler_2 = rotations.CrystalOrientation(*euler_2, angle_type="radians", convention="bunge")
    sym_group = crystallography.SymmetryGroup("432")
    mori = sym_group.misorientation(euler_1, euler_2)
    _, mori_angle = mori.to_axis_angle()
    return mori_angle

def moose_quat_to_euler(quat:list, reorient:bool=False, offset:bool=False) -> list:
    """
    Converts the quaternion outputted by moose into euler-bunge angles

    Parameters:
    * `quat`:     The quaternion
    * `offset`:   Whether to add an offset to phi_1
    * `reorient`: Whether to invert the angle

    Returns the euler-bunge angle (rads)
    """
    euler = rotations.Orientation(quat).to_euler(angle_type="radians", convention="bunge")
    if reorient:
        euler = reorient_euler(euler)
    if offset:
        euler[0] += math.pi
    euler = [fix_angle(e) for e in euler]
    return euler

def reorient_euler(euler:list) -> list:
    """
    Inverts the euler angle from passive/active to active/passive

    Parameters:
    * `euler`: The euler angle (rads)

    Returns the inverted euler angle
    """
    orientation = rotations.CrystalOrientation(euler[0], euler[1], euler[2], angle_type="radians", convention="bunge")
    inverse = orientation.inverse()
    new_euler = inverse.to_euler(angle_type="radians", convention="bunge")
    return list(new_euler)
