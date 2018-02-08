# Module: Topological Neuron Synthesis

# --------------------------------------------
# Generation of artificial neuronal trees
# based on the topology of biological cells
# and their statistical properties
# --------------------------------------------


# Instalation instructions
--------------------------------
# It is suggested to install this module in a visrtual environment
# To create a vistual environment
virtualenv test_syn

# To activate the virtual env
. ./test_syn/bin/activate

# In order to use TNS you need to install:
# - NeuroM from the fork: https://github.com/lidakanari/NeuroM.git
# - TMD from: https://bbpcode.epfl.ch/browse/code/molecularsystems/TMD/

# Example installation of required modules
# 1. create a local directory for neurom
mkdir NeuroMLocal
cd NeuroMLocal

# 2. Clone and install NeuroM branch synthesis_stats
git clone https://github.com/lidakanari/NeuroM.git
cd NeuroM/
git branch --track synthesis_stats origin/synthesis_stats
git checkout synthesis_stats
cd ../..
pip install NeuroMLocal/NeuroM

# 3. create a local directory for TMD
mkdir ../TMDLocal
cd ../TMDLocal

# 4. Clone and install TMD
git clone https://bbpcode.epfl.ch/browse/code/molecularsystems/TMD/
pip install TMDLocal/TMD

# Now you are ready to install TNS synthesizer
cd ..
pip install TNS
