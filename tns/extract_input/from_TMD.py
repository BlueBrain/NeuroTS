import tmd
import numpy as np

def ph_apical(pop, distr, threshold=2):
    """Adds the persistent homology extracted from
    a population of apicals to the distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.apicals]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > threshold)[0]])

    # Add apical key if not in distributions
    if "apical" not in distr:
        distr["apical"] = {}
    
    distr["apical"]["ph"] = phs


def ph_basal(pop, distr, threshold=2):
    """Adds the persistent homology extracted from
    a population of basals to the distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.basals]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > threshold)[0]])

    # Add basal key if not in distributions
    if "basal" not in distr:
        distr["basal"] = {}
    
    distr["basal"]["ph"] = phs


def ph_axon(pop, distr, threshold=2):
    """Adds the persistent homology extracted from
    a population of basals to the distr dictionary
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in pop.axons]

    # Keep only the significant ones
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > threshold)[0]])

    # Add axon key if not in distributions
    if "axon" not in distr:
        distr["axon"] = {}

    distr["axon"]["ph"] = phs

