from scipy import optimize   
import math
import numpy as np
import functools



def env_scaling(x, params):
    return math.exp((x - 1) * params[0]) * params[1] +  params[2]

def env_error(params, pairs):
    return sum([(x[1] - env_scaling(x[0], params))**2 for x in pairs])

def get_scaling_fn(pairs):
    res = optimize.minimize(env_error, args = (vals,), x0 = [0, 0, 0])
    env_error(res.x, vals)
    return functools.partial(env_scaling, params = res.x)

vals = np.array([[0, 0.001],
[0.5, 2.881],
[1, 18]])
out_fn = get_scaling_fn(vals)
for val in vals:
    assert( abs(out_fn(val[0]) - val[1]) < 1e-4)