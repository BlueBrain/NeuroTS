"""Generate diameters."""

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

import morphio, neurom, tmd

from neurots import extract_input

from neurots.generate import diametrizer

k0 = neurom.load_morphology('../test_data/bio/C220197A-P2.h5')
model0 = extract_input.from_diameter.model(k0)

n0 = morphio.mut.Morphology('../test_data/bio/C220197A-P2.h5')
diametrizer.build(n0, diam_method='M1')  # Constant diameters per neurite
n0.write('M1_cell.asc')

n0 = morphio.mut.Morphology('../test_data/bio/C220197A-P2.h5')
diametrizer.build(n0, diam_method='M2')  # Constant diameters per section
n0.write('M2_cell.asc')

n0 = morphio.mut.Morphology('../test_data/bio/C220197A-P2.h5')
diametrizer.build(n0, diam_method='M3')  # Smooth input diameters
n0.write('M3_cell.asc')

n0 = morphio.mut.Morphology('../test_data/bio/C220197A-P2.h5')
diametrizer.build(n0, diam_method='M4', input_model=model0)  # Fix diameters from root
n0.write('M4_cell.asc')

n0 = morphio.mut.Morphology('../test_data/bio/C220197A-P2.h5')
diametrizer.build(n0, diam_method='M5', input_model=model0)  # Fix diameters from tips
n0.write('M5_cell.asc')
