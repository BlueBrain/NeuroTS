"""Some modifiers."""

# Copyright (C) 2021  Blue Brain Project, EPFL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def scale_term_ph(p, rate=1.0):

    def scale_term(p, rate):
        d = np.abs(np.subtract(p[0], p[1]))
        d_star = np.float(d) / rate
        start = np.min([p[0],p[1]])
        new_end = start + d_star
        return [new_end, start] + p[2:]

    return [scale_term(i, rate) for i in p]


def scale_bif_ph(p, rate=1.0):

    def scale_bif(p, rate):
        if np.min([p[0],p[1]]) == 0.0:
            return p
        d = np.abs(np.subtract(p[0], p[1]))
        d_star = np.float(d) / rate
        end = np.max([p[0],p[1]])
        new_start = end - d_star
        return [end, new_start] + p[2:]

    return [scale_bif(i, rate) for i in p]


def elongate_first_ph(p, rate=100):

    def elongate_first(p, rate):
        d = np.abs(np.subtract(p[0], p[1]))
        start = np.min([p[0],p[1]])
        new_start = start + rate
        new_end = new_start + d
        return [new_end, new_start] + p[2:]

    return [elongate_first(i, rate) for i in p]


def multiply_branches_ph(p, length, number_of_branches=2):

    new_p = []
    for i in p:
        d = np.abs(np.subtract(i[0], i[1]))
        if d <= length:
            new_p = new_p + number_of_branches*[i]
        else:
            new_p = new_p + [i]

    return new_p


def filter_small_branches_ph(p, length):
    """Keep only branches greater than the selected length
    """
    new_p = []
    for i in p:
        d = np.abs(np.subtract(i[0], i[1]))
        if d >= length:
            new_p = new_p + [i]

    return new_p


def filter_large_branches_ph(p, length):
    """Keep only branches smaller than the selected length
    """
    new_p = []
    for i in p:
        d = np.abs(np.subtract(i[0], i[1]))
        if d <= length:
            new_p = new_p + [i]

    return new_p


def make_pyramid(p, length):
    """Create a pyramid shape for the barcode
    by reducing the length of the new bar by "length"
    divided by the number of bars from the previous one.
    """
    def sort_ph(ph):
        distances = [np.abs(i[0] - i[1]) for i in ph]
        order = np.argsort(distances).tolist()
        order.reverse()
        ph_sort = np.array(ph)[order]
        return ph_sort.tolist()

    sorted_p = sort_ph(p)
    new_p = [sorted_p[0]]

    size_p = (np.abs(np.subtract(new_p[0][0], new_p[0][1])) / np.float(length)) / (2*(len(p) + 1.))

    for i in sorted_p[1:]:
        if i[1] != 0.0:
            new_p = new_p  + [[new_p[-1][0] - size_p, new_p[-1][1] + size_p] + i[2:]]
        else:
            new_p = new_p  + [[new_p[-1][0] - size_p, 0.0] + i[2:]]

    return new_p


def make_pyramid_symmetric(length, diff, n_branches, angles):
    """Create a pyramid shape for the barcode
    by reducing the length of the new bar by "length"
    divided by the number of bars from the previous one.
    """
    new_p = [[length, 0.0] + angles]
    size_p = diff / n_branches / 2

    for i in xrange(n_branches - 1):
        new_p = new_p  + [[new_p[-1][0] - size_p,
                           new_p[-1][1] + size_p] + angles]

    return new_p


def double_fig(n):
    fig = plt.figure()
    p = ntn.methods.get_ph_neuron(n, neurite_type='basal')
    view.view.neuron3d(n, title='', neurite_type=['basal'], diameter=False, new_fig=False, subplot=(121))
    view.plot.barcode(p, new_fig=False, subplot=(122))
    plt.tight_layout(True)


def double_input(neuron, ph):
    fig = plt.figure()
    view.view.neuron3d(neuron, title='', neurite_type=['basal'], diameter=False, new_fig=False, subplot=(121))
    view.plot.barcode(ph, new_fig=False, subplot=(122))
