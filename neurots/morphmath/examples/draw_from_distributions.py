# Define a set of distributions from which to sample
# Currently the available sampling features are:
# 1. soma_size
# 2. n_neurites
# 3. trunk_orientation_deviations

from distributions import sample
distributions_exemplar = {
    "soma_size": {"norm": {"mean": 8, "std": 1.18}},
    "n_neurites": {"norm": {"mean": 6.75, "std": 1.37}},
    "trunk_orientation_deviation": {"data": {
        "bins":
            [-1.0017981, -0.93768791, -0.87357773, -0.80946755, -0.74535737,
             -0.68124718, -0.617137, -0.55302682, -0.48891663, -0.42480645,
             -0.36069627, -0.29658609, -0.2324759, -0.16836572, -0.10425554,
             -0.04014535, 0.02396483, 0.08807501, 0.1521852, 0.21629538,
             0.28040556, 0.34451574, 0.40862593, 0.47273611, 0.53684629,
             0.60095648, 0.66506666, 0.72917684, 0.79328702, 0.85739721,
             0.92150739, 0.98561757, 1.04972776, 1.11383794, 1.17794812,
             1.2420583, 1.30616849, 1.37027867, 1.43438885, 1.49849904],
        "weights":
            [3., 6., 6., 4., 3., 5., 4., 3., 4., 6., 2., 1., 4.,
             0., 6., 0., 1., 9., 1., 2., 1., 4., 2., 2., 3., 2.,
             2., 1., 1., 2., 2., 2., 3., 1., 1., 3., 0., 3., 1., 2.]}},
}

# import sampler

soma_radius = sample.soma_size(distributions_exemplar)
n_neurites = sample.n_neurites(distributions_exemplar)
trunk_angles = sample.trunk_angles(distributions_exemplar, n_neurites)
