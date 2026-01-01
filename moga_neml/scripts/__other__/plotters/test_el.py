import math, numpy as np
from scipy.optimize import differential_evolution
import matplotlib.pyplot as plt

def run_exp(x:float, a:float, b:float, _:float) -> float:
    return a*math.exp(b*x)

def run_linear(x:float, a:float, b:float, c:float) -> float:
    return c*x + c/b*(1 - math.log(c/a/b))

def get_intercept(a:float, b:float, c:float) -> float:
    return 1/b*math.log(c/a/b)

def get_x_list() -> list:
    return list(np.linspace(-10, 10, 100))

def run_exp_linear(x:float, a:float, b:float, c:float) -> float:
    x_0, x_2 = -10, 10
    x_1 = get_intercept(a, b, c)
    if x_0 < x and x <= x_1:
        return run_exp(x, a, b, c)
    elif x_1 < x and x <= x_2:
        return run_linear(x, a, b, c)
    else:
        return 0

def run_bilinear(x:float):
    a_0, a_1, b_0, b_1 = 14.56, 99.36, 314.46, 690.82
    x_0 = -a_1 / a_0
    x_1 = (b_1 - a_1) / (a_0 - b_0)
    x_2 = 5
    if x_0 < x and x <= x_1:
        return a_0 * x + a_1
    elif x_1 < x and x <= x_2:
        return b_0 * x + b_1
    else:
        return 0

def loss_function(params):
    a, b, c = params
    if c >= a*b:
        return 1e5
    x_list = list(np.linspace(-10, 3, 100))
    loss = np.average([abs(run_bilinear(x) - run_exp_linear(x, a, b, c)) for x in x_list])
    return loss

result = differential_evolution(loss_function, bounds=[(0, 10000), (0, 100), (0, 10000)])
p = result.x
a, b, c = p[0], p[1], p[2]

print("Parameters:", a, b, c)
intercept = get_intercept(a, b, c)
print("Exponential y:", run_exp(intercept, a, b, c))
print("Linear y:", run_linear(intercept, a, b, c))
print("Exponential y':", a*b*math.exp(b*intercept))
print("Linear y':", c)

x_list = get_x_list()
bilinear_y_list = [run_bilinear(x) for x in x_list]
explinear_y_list = [run_exp_linear(x, a, b, c) for x in x_list]

plt.plot(x_list, bilinear_y_list, color="blue", label="Bilinear")
plt.plot(x_list, explinear_y_list, color="red", label="Exponential-linear")
plt.xlim(-8, 2)
plt.legend()
plt.savefig("el.png")
