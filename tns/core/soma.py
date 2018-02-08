'''
TNS class : Soma
'''
import numpy as np

class Soma(object):
    """Soma class"""

    def __init__(self, initial_point=(0.,0.,0.), radius=1.0):
        """TNS Soma Object

        Parameters:
            points: numpy array
        The (x, y, z, d)-coordinates of the x-y surface trace of the soma.
        """
        self.points = [[],]
        self.radius = radius
        self.center = initial_point


    def interpolate(self, points, N=3):
        """Finds the convex hull from a list of points
        and returns a number of points N that belong
        on this convex hull.
        N: sets the minimum number of points to be generated.
        points: initial set of points
        """
        from scipy.spatial import ConvexHull

        hull = ConvexHull(points)

        selected = np.array(points)[hull.vertices]

        if len(selected) > N:
            return selected.tolist()
        elif len(points) > N:
            print 'Warning! Convex hull failed. Original points were saved instead'
            return points.tolist()
        else:
            print 'Warning! Convex hull failed. Original points were saved instead'
            return N*points.tolist()


    def generate(self, neuron, trunk_angles, z_angles, plot_soma=True, interpolation=3):
        """Generates a soma as a sequence of points
        in the circumference of a circle of radius R.
        """
        vectors = []

        sortIDs = np.argsort(trunk_angles)

        angle_norm = 2.*np.pi / len(trunk_angles)

        for i,a in enumerate(np.array(trunk_angles)[sortIDs]):

            phi = np.array(z_angles)[sortIDs][i]
            ang = (i + 1) * angle_norm

            # To smooth out the soma contour we interpolate
            # among the existing soma points:
            # theta = (a + np.array(trunk_angles)[sortIDs][i - 1]) / 2

            theta = a

            vectors.append([self.center[0] + self.radius * \
                            np.cos(theta + ang) * np.sin(phi),
                            self.center[1] + self.radius * \
                            np.sin(theta + ang) * np.sin(phi),
                            self.center[2]]) # Make soma a 2D contour
                            # For a 3d contour replace with 
                            # self.center[1] + self.radius * \
                            # np.cos(phi)

        if interpolation is None:
            self.points = [np.append(v, [0.]) for v in vectors]
        else:
            new_vectors = self.interpolate(np.array(vectors)[:, :2], interpolation)
            self.points = [np.append(v, [self.center[2], 0.]) for v in new_vectors]

        neuron.points = neuron.points + self.points
        neuron.soma = self

        return np.array(vectors)


