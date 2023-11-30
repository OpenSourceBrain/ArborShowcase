#!/usr/bin/env python3

import arbor
import sys

# (1) Create a morphology with a single (cylindrical) segment of length=diameter=6 μm
tree = arbor.segment_tree()
tree.append(arbor.mnpos, arbor.mpoint(-3, 0, 0, 3), arbor.mpoint(3, 0, 0, 3), tag=1)

# (2) Define the soma and its midpoint
labels = arbor.label_dict({'soma':   '(tag 1)',
                           'midpoint': '(location 0 0.5)'})

# (3) Create cell and set properties
decor = arbor.decor()
decor.set_property(Vm=-65)
decor.paint('"soma"', arbor.density('hh'))
decor.paint('"soma"', arbor.density('pas'))
decor.place('"midpoint"', arbor.iclamp( 5, 25, 0.02), 'iclamp')
decor.place('"midpoint"', arbor.threshold_detector(-10), 'detector')

# (4) Create cell and the single cell model based on it
cell = arbor.cable_cell(tree, labels=labels, decor=decor)

# (5) Make single cell model.
m = arbor.single_cell_model(cell)

# (6) Attach voltage probe sampling at 10 kHz (every 0.1 ms).
m.probe('voltage', '"midpoint"', frequency=10000)

# (7) Run simulation for 50 ms of simulated activity.
m.run(tfinal=50)

# (8) Print spike times.
if len(m.spikes)>0:
    print('{} spikes:'.format(len(m.spikes)))
    for s in m.spikes:
        print('{:3.3f}'.format(s))
else:
    print('no spikes')

file_of = open("simple.dat", 'w')

for i in zip(m.traces[0].time, m.traces[0].value):
    file_of.write('%s\t%s\n'%(i[0]/1000,i[1]/1000))
file_of.close()

if not '-nogui' in sys.argv:
    import matplotlib.pylab as plt
    # (8) Plot the recorded voltages over time.
    print("Plotting results ...")


    #seaborn.set_theme() # Apply some styling to the plot
    plt.plot(m.traces[0].time, m.traces[0].value, )

    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage (mV)')

    plt.show()
