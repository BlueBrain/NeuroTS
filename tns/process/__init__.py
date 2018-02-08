# Module to generate diameters for a set of tree-shaped cells, using biological data.

def diametrize(input_file, cell_name, new_name=None):
    '''Extracts the model for the diametrization from the input_file
       and replaces the diameters of the cell_name neuron accordingly.
    '''
    import diameter_model
    import diametrizer
    import neurom as nm

    neuron_input = nm.load_neuron(input_file)
    neuron_to_modify = diametrizer.load_h5(cell_name)

    model = diameter_model.diameter_model(neuron_input)

    diametrizer.diametrize(neuron_to_modify, model=model)

    if new_name is None:
        neuron_to_modify.name = neuron_to_modify.name + '_diam'
    else:
        neuron_to_modify.name = new_name

    neuron_to_modify.save()
