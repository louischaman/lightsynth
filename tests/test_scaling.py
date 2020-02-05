from utils import env_scaling

vals = [[0, 0.001],
[0.5, 2.881],
[1, 18]]
out_fn = env_scaling.get_scaling_fn(vals)
for val in vals:
    assert( abs(out_fn(val[0]) - val[1]) < 1e-4)