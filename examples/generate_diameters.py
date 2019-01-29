import morphio, neurom, tmd

from tns import extract_input

from tns.generate.diametrizer import diametrize_constant_all, diametrize_constant, diametrize_smoothing, diametrize_from_tips, diametrize_from_root

k0 = neurom.load_neuron('./Input_cells/C060114A5.h5')
model0 = extract_input.from_diameter.model(k0)

n0 = morphio.mut.Morphology('./Output_cells/C060114A5.h5')
diametrize_constant(n0)
n0.write('test_algo1.asc')

n0 = morphio.mut.Morphology('./Output_cells/C060114A5.h5')
diametrize_constant_all(n0)
n0.write('test_algo2.asc')

n0 = morphio.mut.Morphology('./Output_cells/C060114A5.h5')
diametrize_smoothing(n0)
n0.write('test_algo3.asc')

n0 = morphio.mut.Morphology('./Output_cells/C060114A5.h5')
diametrize_from_tips(n0, model0)
n0.write('test_algo4.asc')

n0 = morphio.mut.Morphology('./Output_cells/C060114A5.h5')
diametrize_from_root(n0, model0)
n0.write('test_algo5.asc')
