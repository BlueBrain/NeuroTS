import tmd
import numpy as np

def ph_apical(pop, Distr):
    """Adds the persistent homology extracted from
    a population of apicals to the Distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.apicals]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > 2)[0]])

    if "apical" not in Distr:
        Distr["apical"] = {"ph": phs}
    else:
        Distr["apical"]["ph"] = phs


def ph_basal(pop, Distr):
    """Adds the persistent homology extracted from
    a population of basals to the Distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.basals]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > 2)[0]])

    if "basal" not in Distr:
        Distr["basal"] = {"ph": phs}
    else:
        Distr["basal"]["ph"] = phs


def ph_axon(pop, Distr):
    """Adds the persistent homology extracted from
    a population of basals to the Distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.axons]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > 10)[0]])

    if "axon" not in Distr:
        Distr["axon"] = {"ph": phs}
    else:
        Distr["axon"]["ph"] = phs

