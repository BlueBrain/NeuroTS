import numpy as np
from tns.morphmath import random_tree as rd
from tns.basic import round_num

bif_methods = {'bio_oriented': rd.get_bif_bio_oriented,
               'symmetric': rd.get_bif_symmetric,
               'directional': rd.get_bif_directional, 
               'random': rd.get_bif_random}
