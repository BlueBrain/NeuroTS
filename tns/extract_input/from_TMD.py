import tmd
import numpy as np


def persistent_homology_angles(pop, threshold=2, neurite_type='basals'):
    """Adds the persistent homology extracted from
    a population of apicals to the distr dictionary
    Each tree in the population is associated with a persistence barcode (diagram)
    and a set of angles that will be used as input for synthesis.
    """
    ph_ang = [tmd.methods.get_ph_angles(tr) for tr in getattr(pop, neurite_type)]

    # Keep only the trees whose number of terminations is above the threshold
    # Saves the list of persistence diagrams for the selected neurite_type
    phs = list(np.array(ph_ang)[np.where(np.array([len(p) for p in ph_ang] ) > threshold)[0]])

    return {"persistence_diagram": phs}
