#!/usr/bin/env python3

import arbor
import pandas, seaborn
from math import sqrt


def make_cable_cell(gid):
    # (1) Build a segment tree
    tree = arbor.segment_tree()

    # Soma (tag=1) with radius 6 μm, modelled as cylinder of length 2*radius
    s = tree.append(arbor.mnpos, arbor.mpoint(-12, 0, 0, 6), arbor.mpoint(0, 0, 0, 6), tag=1)

    # Single dendrite (tag=3) of length 50 μm and radius 2 μm attached to soma.
    b0 = tree.append(s, arbor.mpoint(0, 0, 0, 2), arbor.mpoint(50, 0, 0, 2), tag=3)

    # Attach two dendrites (tag=3) of length 50 μm to the end of the first dendrite.
    # Radius tapers from 2 to 0.5 μm over the length of the dendrite.
    b1 = tree.append(b0, arbor.mpoint(50, 0, 0, 2), arbor.mpoint(50+50/sqrt(2), 50/sqrt(2), 0, 0.5), tag=3)
    # Constant radius of 1 μm over the length of the dendrite.
    b2 = tree.append(b0, arbor.mpoint(50, 0, 0, 1), arbor.mpoint(50+50/sqrt(2), -50/sqrt(2), 0, 1), tag=3)

    # Associate labels to tags
    labels = arbor.label_dict()
    labels['soma'] = '(tag 1)'
    labels['dend'] = '(tag 3)'

    # (2) Mark location for synapse at the midpoint of branch 1 (the first dendrite).
    labels['synapse_site'] = '(location 1 0.5)'
    # Mark the root of the tree.
    labels['root'] = '(root)'

    # (3) Create a decor and a cable_cell
    decor = arbor.decor()

    # Put hh dynamics on soma, and passive properties on the dendrites.
    decor.paint('"soma"', arbor.density('hh'))
    decor.paint('"dend"', arbor.density('pas'))

    # (4) Attach a single synapse.
    decor.place('"synapse_site"', arbor.synapse('expsyn'), 'syn')

    # Attach a spike detector with threshold of -10 mV.
    decor.place('"root"', arbor.threshold_detector(-10), 'detector')

    cell = arbor.cable_cell(tree, labels=labels, decor=decor)

    return cell

# (5) Create a recipe that generates a network of connected cells.
class custom_recipe(arbor.recipe):

    def __init__(self):
        # The base C++ class constructor must be called first, to ensure that
        # all memory in the C++ class is initialized correctly.
        arbor.recipe.__init__(self)
        self.props = arbor.neuron_cable_properties()

    def set_num_cells(self, ncells):

        self.ncells = ncells

    # (6) The num_cells method that returns the total number of cells in the model
    # must be implemented.
    def num_cells(self):
        return self.ncells

    # (7) The cell_description method returns a cell
    def cell_description(self, gid):
        return make_cable_cell(gid)

    # The kind method returns the type of cell with gid.
    # Note: this must agree with the type returned by cell_description.
    def cell_kind(self, gid):
        return arbor.cell_kind.cable

    # (8) Make a ring network. For each gid, provide a list of incoming connections.
    def connections_on(self, gid):
        src = (gid-1)%self.ncells
        w = 0.01
        d = 5
        return [arbor.connection((src,'detector'), 'syn', w, d)]

    def num_targets(self, gid):
        return 1

    def num_sources(self, gid):
        return 1

    # (9) Attach a generator to the first cell in the ring.
    def event_generators(self, gid):
        if gid==0:
            sched = arbor.explicit_schedule([1])
            weight = 0.1
            return [arbor.event_generator('syn', weight, sched)]
        return []

    # (10) Place a probe at the root of each cell.
    def probes(self, gid):
        return [arbor.cable_probe_membrane_voltage('"root"')]

    def global_properties(self, kind):
        return self.props

# (11) Instantiate recipe
ncells = 4
recipe = custom_recipe()
recipe.set_num_cells(ncells)

# (12) Create a default execution context, domain decomposition and simulation
context = arbor.context()
decomp = arbor.partition_load_balance(recipe, context)
sim = arbor.simulation(recipe, domains=decomp, context=context)

# (13) Set spike generators to record
sim.record(arbor.spike_recording.all)

# (14) Attach a sampler to the voltage probe on cell 0.
handles = [sim.sample((gid, 0), arbor.regular_schedule(0.01)) for gid in range(ncells)]

# (15) Run simulation
sim.run(80)
print('Simulation finished')

# (16) Print spike times
print('spikes:')
for sp in sim.spikes():
    print(' ', sp)

# (17) Plot the recorded voltages over time.
print("Plotting results ...")
df_list = []
for gid in range(ncells):
    samples, meta = sim.samples(handles[gid])[0]
    # Broken!
    #df_list.append(pandas.DataFrame({'t/ms': samples[:, 0], 'U/mV': samples[:, 1], 'Cell': f"cell {gid}"}))

#df = pandas.concat(df_list)
#seaborn.relplot(data=df, kind="line", x="t/ms", y="U/mV",hue="Cell",ci=None).savefig('custom_net_result.png')
