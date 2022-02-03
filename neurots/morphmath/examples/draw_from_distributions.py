"""Define a set of distributions from which to sample.

Currently the available sampling features are:
1. soma_size
2. n_neurites
3. trunk_orientation_deviations
"""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from distributions import sample

distributions_exemplar = {
    "soma_size": {"norm": {"mean": 8, "std": 1.18}},
    "n_neurites": {"norm": {"mean": 6.75, "std": 1.37}},
    "trunk_orientation_deviation": {
        "data": {
            "bins": [
                -1.0017981,
                -0.93768791,
                -0.87357773,
                -0.80946755,
                -0.74535737,
                -0.68124718,
                -0.617137,
                -0.55302682,
                -0.48891663,
                -0.42480645,
                -0.36069627,
                -0.29658609,
                -0.2324759,
                -0.16836572,
                -0.10425554,
                -0.04014535,
                0.02396483,
                0.08807501,
                0.1521852,
                0.21629538,
                0.28040556,
                0.34451574,
                0.40862593,
                0.47273611,
                0.53684629,
                0.60095648,
                0.66506666,
                0.72917684,
                0.79328702,
                0.85739721,
                0.92150739,
                0.98561757,
                1.04972776,
                1.11383794,
                1.17794812,
                1.2420583,
                1.30616849,
                1.37027867,
                1.43438885,
                1.49849904,
            ],
            "weights": [
                3.0,
                6.0,
                6.0,
                4.0,
                3.0,
                5.0,
                4.0,
                3.0,
                4.0,
                6.0,
                2.0,
                1.0,
                4.0,
                0.0,
                6.0,
                0.0,
                1.0,
                9.0,
                1.0,
                2.0,
                1.0,
                4.0,
                2.0,
                2.0,
                3.0,
                2.0,
                2.0,
                1.0,
                1.0,
                2.0,
                2.0,
                2.0,
                3.0,
                1.0,
                1.0,
                3.0,
                0.0,
                3.0,
                1.0,
                2.0,
            ],
        }
    },
}

# import sampler

soma_radius = sample.soma_size(distributions_exemplar)
n_neurites = sample.n_neurites(distributions_exemplar)
trunk_angles = sample.trunk_angles(distributions_exemplar, n_neurites)
