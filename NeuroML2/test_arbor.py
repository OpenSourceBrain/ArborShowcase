import arbor
import numpy as np
import matplotlib.pyplot as plt

cell_id = 'BallAndStick'
nml = arbor.neuroml('%s.cell.nml'%cell_id)

cell_ids = nml.cell_ids()
morpho_data = nml.cell_morphology(cell_id)
morpho = morpho_data.morphology

# Get the region label dictionaries associated with the morphology.
morpho_segments = morpho_data.segments()
morpho_named = morpho_data.named_segments() # (label_dict)
morpho_groups = morpho_data.groups()

# Create new label dict add to it all the NeuroML dictionaries.
labels = arbor.label_dict()
labels.append(morpho_segments)
labels.append(morpho_named)
labels.append(morpho_groups)

print(nml)
# >>> print([reg for reg in labels.regions if not reg.isdigit()])
# ['all', 'soma_group', 'dendrite_group', 'axon_group', ...]

# Add locsets to the label dictionary.
labels['stim_site'] = '(location 0 0.5)' # site for the stimulus
#labels['axon_end']  = '(restrict (terminal) (region "axon_group"))' # end of the axon.

if arbor.__version__.startswith('0.9'):
    labels['dend_end']  = '(restrict-to (terminal) (region "dendrite_group"))' # end of the dend.
else:
    labels['dend_end']  = '(restrict (terminal) (region "dendrite_group"))' # end of the dend.

labels['root']      = '(root)' # the start of the soma in this morphology is at the root of the cell.


labels['soma'] = '(location 0 0.5)'
#labels['dend1'] = '(location 1 0.5)'
#labels['dend2'] = '(location 2 0.5)'

print("Current labels:")
for l in labels:
    print("  Label %s: %s"% (l, labels[l]))

decor = arbor.decor()

decor.paint('"all"', arbor.density('pas', dict(g=2.01e-05)))

decor.place('"stim_site"', arbor.iclamp( 100, 200, 0.1), 'iclamp')



# Combine morphology with region and locset definitions to make a cable cell.
cell = arbor.cable_cell(morpho, labels=labels, decor=decor)
print(cell.locations('"dend_end"'))

# Make single cell model.
m = arbor.single_cell_model(cell)

m.probe('voltage', where='"root"',  frequency=500)
m.probe('voltage', where='"dend_end"',  frequency=500)


# Simulate the cell
print('Simulation start.')
tfinal = 1000 # ms
m.run(tfinal)
print('Simulation done.')


# Print spike times.
if len(m.spikes)>0:
    print('{} spikes:'.format(len(m.spikes)))
    for s in m.spikes:
        print('  {:7.4f}'.format(s))
else:
    print('no spikes')

for tr in m.traces:
    print(tr)
    x = np.array(tr.value)
    t = np.array(tr.time)
    plt.plot(t, x, label=tr.location)

    with open('%s.dat'%str(tr.location).replace(' ','_').replace('(','_').replace(')','_'),'w') as f:
        for ti in range(len(t)):
            f.write('%s\t%s\n'%(t[ti]/1000.0,x[ti]/1000.0))
plt.legend()
plt.show()
