
# Libraries
import numpy as np
import matplotlib.pyplot as plt

def get_damage(a_0:float, a_1:float, b_0:float, b_1:float):
    """
    Gets the damage interpolation bilinear curve
    
    Parameters:
    * `a_0`: Gradient for left side of bilinear function
    * `a_1`: Vertical intercept for left side of bilinear function
    * `b_0`: Gradient for right side of bilinear function
    * `b_1`: Vertical intercept for right side of bilinear function
    
    Returns the x and y coordinates (on the log10-log10 scale)
    """
    
    # Get x values
    x_0 = -a_1 / a_0                # x intercept of left line and x axis
    x_1 = (b_1 - a_1) / (a_0 - b_0) # x intercept of two lines
    x_2 = 3                         # x intercept of right line and y axis
    
    # Get y values
    y_0 = 0                         # y intercept of left line and x axis
    y_1 = a_0 * x_1 + a_1           # y intercept of two lines
    y_2 = b_0 * x_2 + b_1           # y intercept of right line and y axis
    
    # Combine, log, and return
    num_points = 16
    x_list = list(np.linspace(x_0, x_1, num_points)) + list(np.linspace(x_1, x_2, num_points))
    y_list = list(np.linspace(y_0, y_1, num_points)) + list(np.linspace(y_1, y_2, num_points))
    return x_list, y_list

params_str = """
2.1462	24.063	167.25	4.6886	341.18	712.26

"""
params_list = [list(map(float, line.split())) for line in params_str.strip().split("\n")]

for params in params_list:
    x_list, y_list = get_damage(*params)
    plt.plot(x_list, y_list)
plt.xlim(-8, 0)
plt.ylim(-100, 500)
plt.savefig("prd.png")
