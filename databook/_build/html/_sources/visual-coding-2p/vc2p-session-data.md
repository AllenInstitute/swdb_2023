---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt
```
```{code-cell} ipython3
from allensdk.core.brain_observatory_cache import BrainObservatoryCache
boc = BrainObservatoryCache()
```

# Getting data from a session

We're going to examine the data available for a single session. First, let's identify the session from the experiment container we explored in vc2p-dataset in which that "natural scenes" stimulus was presented.

```{code-cell} ipython3
experiment_container_id = 511510736
session_id = boc.get_ophys_experiments(experiment_container_ids=[experiment_container_id], stimuli=['natural_scenes'])[0]['id']
```

We can use this session_id to get all the data contained in the NWB for this session using <b>get_ophys_experiment_data</b>

```{code-cell} ipython3
data_set = boc.get_ophys_experiment_data(ophys_experiment_id=session_id)
```

## Maximum projection
This is the projection of the full motion corrected movie. It shows all of the cells imaged during the session.

```{code-cell} ipython3
max_projection = data_set.get_max_projection()
```

```{code-cell} ipython3
fig = plt.figure(figsize=(6,6))
plt.imshow(max_projection, cmap='gray')
plt.axis('off')
```

## ROI Masks
{term}`ROI`s are all of the segmented masks for cell bodies identified in this session.

```{code-cell} ipython3
rois = data_set.get_roi_mask_array()
```

What is the shape of this array? How many neurons are in this experiment?

```{code-cell} ipython3
rois.shape
```

The first dimension of this array is the number of neurons, and each element of this axis is the mask of an individual neuron

Plot the masks for all the ROIs.

```{code-cell} ipython3
fig = plt.figure(figsize=(6,6))
plt.imshow(rois.sum(axis=0))
plt.axis('off');
```

## Fluorescence and DF/F traces
The NWB file contains a number of traces reflecting the processing that is done to the extracted fluorescence before we analyze it. The fluorescence traces are the mean fluorescence of all the pixels contained within a ROI mask.

There are a number of activity traces accessible in the NWB file, including raw fluorescence, neuropil corrected traces, demixed traces, and DF/F traces. 

```{code-cell} ipython3
timestamps,fluor = data_set.get_fluorescence_traces()
```

To correct from contamination from the neuropil, we perform neuropil correction. First, we extract a local neuropil signal, by creating a neuropil mask that is an annulus around the ROI mask (without containing any pixels from nearby neurons). You can see these neuropil signals in the neuropil traces:

```{code-cell} ipython3
timestamps, np = data_set.get_neuropil_traces()
```

This neuropil trace is subtracted from the fluorescence trace, after being weighted by a factor that is computed for each neuron. The resulting corrected fluorescence trace is accessed here:

```{code-cell} ipython3
timestamps,cor = data_set.get_corrected_fluorescence_traces()
```

Let's look at these traces for one cell:

```{code-cell} ipython3
fig = plt.figure(figsize=(8,3))
plt.plot(timestamps, fluor[122,:])
plt.plot(timestamps, np[122,:])
plt.plot(timestamps, cor[122,:])
plt.xlabel("Time (s)")
plt.xlim(1900,2200)
```

(demixing?)

The signal we are most interested in the the DF/F - the change in fluorescence normalized by the baseline fluorescence. 

```{code-cell} ipython3
ts, dff = data_set.get_dff_traces()
```

```{code-cell} ipython3
fig = plt.figure(figsize=(8,3))
plt.plot(ts, dff[122,:], color='gray')
plt.xlabel("Time (s)")
plt.xlim(1900,2200)
plt.ylabel("DFF")
```

## Extracted events
As of the October 2018 data release, we are providing access to events extracted from the DF/F traces using the L0 method developed by Sean Jewell and Daniella Witten. 
```{note} 
The extracted events are not stored in the NWB file, thus aren't a function of the data_set object, but are available through the boc
```

```{code-cell} ipython3
events = boc.get_ophys_experiment_events(ophys_experiment_id=session_id)
```

```{code-cell} ipython3
fig = plt.figure(figsize=(8,3))
plt.plot(ts, dff[122,:], color='gray')
plt.plot(ts, 2*events[122,:]+5, color='black')
plt.xlabel("Time (s)")
plt.xlim(1900,2200)
plt.ylabel("DFF")
```

## Stimulus epochs

Several stimuli are shown during each imaging session, interleaved with each other. The stimulus epoch table provides information of these interleaved stimulus epochs, revealing when each epoch starts and ends. The start and end here are provided in terms of the imaging frame of the two-photon imaging. This allows us to index directly into the dff or event traces.

```{code-cell} ipython3
stim_epoch = data_set.get_stimulus_epoch_table()
stim_epoch
```

Let's plot the DFF traces of a number of cells and overlay stimulus epochs.  

```{code-cell} ipython3
fig = plt.figure(figsize=(14,8))

#here we plot the first 50 neurons in the session
for i in range(50):
    plt.plot(dff[i,:]+(i*2), color='gray')
    
#here we shade the plot when each stimulus is presented
colors = ['blue','orange','green','red']
for c,stim_name in enumerate(stim_epoch.stimulus.unique()):
    stim = stim_epoch[stim_epoch.stimulus==stim_name]
    for j in range(len(stim)):
        plt.axvspan(xmin=stim.start.iloc[j], xmax=stim.end.iloc[j], color=colors[c], alpha=0.1)
```

## Running speed

The running speed of the animal on the rotating disk during the entire session. This has been temporally aligned to the two photon imaging, which means that this trace has the same length as dff (etc). This also means that the same stimulus start and end information indexes directly into this running speed trace.

```{code-cell} ipython3
dxcm, timestamps = data_set.get_running_speed()
print("length of dff: ", str(len(dff)))
print("length of running speed: ", str(len(dxcm)))
```

Plot the running speed. 

```{code-cell} ipython3
plt.plot(dxcm)
plt.ylabel("Running speed (cm/s)", fontsize=18)
```

Add the running speed to the neural activity and stimulus epoch figure

```{code-cell} ipython3
fig = plt.figure(figsize=(14,10))
for i in range(50):
    plt.plot(dff[i,:]+(i*2), color='gray')
plt.plot((0.2*dxcm)-20)
    
#for each stimulus, shade the plot when the stimulus is presented
colors = ['blue','orange','green','red']
for c,stim_name in enumerate(stim_epoch.stimulus.unique()):
    stim = stim_epoch[stim_epoch.stimulus==stim_name]
    for j in range(len(stim)):
        plt.axvspan(xmin=stim.start.iloc[j], xmax=stim.end.iloc[j], color=colors[c], alpha=0.1)
```
## Stimulus Table and Template
Each stimulus that is shown has a <b>stimulus table</b> that details what each trial is and when it is presented. Additionally, the <b>natural scenes</b>, <b>natural movies</b>, and <b>locally sparse noise</b> stimuli have a <b>stimulus template</b> that shows the exact image that is presented to the mouse. We detail how to access and use these items in [Visual stimuli](vc2p-stimuli.md).

## Cell ids and indices

Each neuron in the dataset has a unique id, called the <b>cell specimen id</b>. To find the neurons in this session, get the cell specimen ids. This id can also be used to identify experiment containers or sessions where a given neuron is present

```{code-cell} ipython3
cell_ids = data_set.get_cell_specimen_ids()
cell_ids
```

Within each individual session, a cell id is associated with an index. This index maps into the dff or event traces.  Pick one cell id from the list above and find the index for that neuron. 

```{code-cell} ipython3
data_set.get_cell_specimen_indices([517473110])
```

```{note}
As neurons are often matched across sessions, that neuron will have the same cell specimen id in all said sessions, but it will have a different cell specimen index in each session. This is explored in [Cross session data](vc2p-cross-session-data.md).
```


