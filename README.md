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
# - TMD from: https://bbpcode.epfl.ch/code/molecularsystems/TMD

# Installation of modules required for TNS input
# 1. Clone NeuroM to a local directory
git clone https://github.com/lidakanari/NeuroM.git

# 2. Install NeuroM branch synthesis_stats
cd NeuroM/
git branch --track synthesis_stats origin/synthesis_stats
git checkout synthesis_stats
cd ..
pip install NeuroM

# 3. Clone TMD to a local directory
git clone https://bbpcode.epfl.ch/code/molecularsystems/TMD

# 4. Clone and install TMD
pip install TMD

# Now you are ready to install TNS synthesizer
git clone https://bbpcode.epfl.ch/code/molecularsystems/TNS
pip install TNS
