import morphio, neurom, tmd

from tns import extract_input

from tns.generate import diametrizer

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