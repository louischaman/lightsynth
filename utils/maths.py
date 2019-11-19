
import math
import functools

def sign(x):
    return int(math.copysign(1, x))

def linear_scaling(x, new_min, new_max, old_min, old_max):
    # linear scaling from (old_min, old_max) to (new_min, new_max)
    return (((x - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min

linear_scaling_in_01 = functools.partial(linear_scaling, old_min=0, old_max=1)

def exp_scaling_0_max(x, max_val, exp_rate):
    # scales input in range (0,1) to range (0,max_val) exponentially so more control in low end
    return max_val * ( math.pow(exp_rate, x) - 1 ) /(exp_rate - 1)

def exp_scaling_min_max(x, min_val, max_val, exp_rate):
    # scales input in range (0,1) to range (min_value, max_val) exponentially so more control in low end
    assert(max_val > min_val)
    out_range = max_val - min_val
    return exp_scaling_0_max(x, max_val = out_range, exp_rate = exp_rate) + min_val