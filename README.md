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
```bash
git clone ssh://bbpcode.epfl.ch/molecularsystems/TNS
pip install ./TNS --process-dependency-links
```
