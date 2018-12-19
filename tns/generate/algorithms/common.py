import numpy as np
from tns.morphmath import random_tree as rd
from tns.basic import round_num

bif_methods = {'bio_oriented': rd.get_bif_bio_oriented,
               'symmetric': rd.get_bif_symmetric,
               'directional': rd.get_bif_directional,
               'random': rd.get_bif_random}


def init_ph_angles(ph_angles):
    '''Returns the data to be used by TMD algorithms
    in the growth process.
    '''
    bif = [round_num(i) for i in np.unique(np.array(ph_angles)[:, 1])[1:]]  # bif[0] = 0 trivial.
    term = [round_num(i) for i in np.array(ph_angles)[:, 0]]
    angles = {round_num(p[1]): [p[2], p[3], p[4], p[5]] for p in ph_angles}
    bt_all = {round_num(p[1]): p[0] for p in ph_angles}

    return bif, term, angles, bt_all
