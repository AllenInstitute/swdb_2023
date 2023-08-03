---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: allensdk
  language: python
  name: allensdk
---

# Units

 The primary data in this dataset is the recorded acrtivity of isolated units. A
 number of metrics are used to isolate units through spike sorting, and these
 metrics can be used to access how well isolated they are and the quality of
 each unit. The `units` dataframe provides many of these metrics, as well as
 parameterization of the waveform for each unit that passed initial QC,
 including

* **firing rate:** mean spike rate during the entire session
* **presence ratio:** fraction of session when spikes are present
* **ISI violations:** rate of refractory period violations
* **Isolation distances:** distance to nearest cluster in Mihalanobis space
* **d':** classification accuracy based on LDA
* **SNR:** signal to noise ratio
* **Maximum drift:** Maximum change in spike depth during recording
* **Cumulative drift:** Cumulative change in spike depth during recording

## Accessing the units

```{code-cell} ipython3
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
```

```{code-cell} ipython3
# Example cache directory path, it determines where downloaded data will be stored
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
```

```{code-cell} ipython3
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
session_id = 750332458 # An example session id
session = cache.get_session_data(session_id)
```

**1D Waveform features:**

```{image} ../../resources/spike_waveform.png
:name: spike-waveform
```

For more information on these:

https://github.com/AllenInstitute/ecephys_spike_sorting/tree/master/ecephys_spike_sorting/modules/quality_metrics
https://github.com/AllenInstitute/ecephys_spike_sorting/tree/master/ecephys_spike_sorting/modules/mean_waveforms


:::{admonition} Example: Units
Get the `units` dataframe for this session.

What the the metrics? (i.e. what are the columns for the dataframe?

How many units are there? How many units per structure?
:::

```{code-cell} ipython3
:tags: [output_scroll]
session.units.head()
```

```{code-cell} ipython3
:tags: [output_scroll]
session.units.columns
```

How many units are in this session?

```{code-cell} ipython3
session.units.shape[0]
```

Which areas (structures) are they from?

```{code-cell} ipython3
print(session.units.ecephys_structure_acronym.unique())
```

How many units per area are there?

```{code-cell} ipython3
session.units.ecephys_structure_acronym.value_counts()
```

:::{admonition} Example: Select 'good' units
A default is to include units that have a SNR greater than 1 and ISI violations
less than 0.5 Plot a histogram of the values for each of these metrics? How
many units meet these criteria? How many per structure?
:::


plot a histogram for SNR

```{code-cell} ipython3
plt.hist(session.units.snr, bins=30);
```

plot a histogram for ISI violations

```{code-cell} ipython3
plt.hist(session.units.isi_violations, bins=30);
```

```{code-cell} ipython3
good_units = session.units[(session.units.snr>1)&(session.units.isi_violations<0.5)]
len(good_units)
```

```{code-cell} ipython3
good_units.ecephys_structure_acronym.value_counts()
```

:::{admonition} Example: Compare the firing rate of good units in different structures
Make a violinplot of the overall firing rates of units across structures.
:::

```{code-cell} ipython3
import seaborn as sns
```

```{code-cell} ipython3
sns.violinplot(y='firing_rate', x='ecephys_structure_acronym',data=good_units)
```

:::{admonition} Example: Plot the location of the units on the probe
Color each structure a different color. What do you learn about the vertical position values?
:::

```{code-cell} ipython3
plt.figure(figsize=(8,6))
# restrict to one probe
probe_id = good_units.probe_id.values[0]
probe_units = good_units[good_units.probe_id==probe_id]
for structure in good_units.ecephys_structure_acronym.unique():
    plt.hist(
        probe_units[probe_units.ecephys_structure_acronym==structure].probe_vertical_position.values,
        bins=100, range=(0,3200), label=structure
    )
plt.legend()
plt.xlabel('Probe vertical position (mm)', fontsize=16)
plt.ylabel('Unit count', fontsize=16)
plt.show()
```

### Spike Times

The primary data in this dataset is the recorded acrtivity of isolated units.
The `spike times` is a dictionary of spike times for each units in the session.

:::{admonition} Example: Spike Times
Next let's find the `spike_times` for these units.
:::

```{code-cell} ipython3
spike_times = session.spike_times
```

What type of object is this?

```{code-cell} ipython3
type(spike_times)
```

How many items does it include?

```{code-cell} ipython3
len(spike_times)
```

```{code-cell} ipython3
len(session.units)
```

What are the keys for this object?

```{code-cell} ipython3
list(spike_times.keys())[:5]
```

These keys are unit ids. Use the unit_id for the first unit to get the spike times for that unit. How many spikes does it have in the entire session?

```{code-cell} ipython3
spike_times[session.units.index[0]]
```

```{code-cell} ipython3
print(len(spike_times[session.units.index[0]]))
```

:::{admonition} Example: Get the spike times for the units in V1
Use the units dataframe to identify units in 'VISp' and use the spike_times to
get their spikes. Start just getting the spike times for the first unit
identified this way. Plot a raster plot of the spikes during the first 5
minutes (300 seconds) of the experiment.
:::

```{code-cell} ipython3
:tags: [output_scroll]
session.units[session.units.ecephys_structure_acronym=='VISp'].head()
```

```{code-cell} ipython3
unit_id = session.units[session.units.ecephys_structure_acronym=='VISp'].index[12]
```

```{code-cell} ipython3
spikes = spike_times[unit_id]
plt.figure(figsize=(15,4))
plt.plot(spikes, np.repeat(0,len(spikes)), '|')
plt.xlim(0,300)
plt.xlabel("Time (s)")
```

:::{admonition} Example: Plot the firing rate for this units across the entire session
A raster plot won't work for visualizing the activity across the entire session
as there are too many spikes! Instead, bin the activity in 1 second bins.
:::

```{code-cell} ipython3
numbins = int(np.ceil(spikes.max()))
binned_spikes = np.empty((numbins))
for i in range(numbins):
    binned_spikes[i] = len(spikes[(spikes>i)&(spikes<i+1)])
```

```{code-cell} ipython3
plt.figure(figsize=(20,5))
plt.plot(binned_spikes)
plt.xlabel("Time (s)")
plt.ylabel("FR (Hz)")
```

:::{admonition} Example: Plot firing rates for units in V1
 Now let's do this for up to 50 units in V1. Make an array of the binned activity of all units in V1 called 'v1_binned'. We'll use this again later.
:::

```{code-cell} ipython3
v1_units = session.units[session.units.ecephys_structure_acronym=='VISp']
numunits = len(v1_units)
if numunits>50:
    numunits=50
v1_binned = np.empty((numunits, numbins))
for i in range(numunits):
    unit_id = v1_units.index[i]
    spikes = spike_times[unit_id]
    for j in range(numbins):
        v1_binned[i,j] = len(spikes[(spikes>j)&(spikes<j+1)])
```

Plot the activity of all the units, one above the other

```{code-cell} ipython3
plt.figure(figsize=(20,10))
for i in range(numunits):
    plt.plot(i+(v1_binned[i,:]/30.), color='gray')
```

### Unit waveforms

For each unit, the average action potential waveform has been recorded from each
channel of the probe. This is contained in the `mean_waveforms` object. This is
the characteristic pattern that distinguishes each unit in spike sorting, and it
can also help inform us regarding differences between cell types.

We will use this in conjuction with the `channel_structure_intervals` function
which tells us where each channel is located in the brain. This will let us get
a feel for the spatial extent of the extracellular action potential waveforms in
relation to specific structures.

:::{admonition} Example: Unit waveforms
Get the waveform for one unit.
:::

```{code-cell} ipython3
waveforms = session.mean_waveforms
```

What type of object is this?

```{code-cell} ipython3
type(waveforms)
```

What are the keys?

```{code-cell} ipython3
list(waveforms.keys())[:5]
```

Get the waveform for one unit

```{code-cell} ipython3
unit = session.units.index.values[400]
wf = session.mean_waveforms[unit]
```

What type of object is this? What is its shape?

```{code-cell} ipython3
type(wf)
```

```{code-cell} ipython3
wf.coords
```

```{code-cell} ipython3
wf.shape
```

```{code-cell} ipython3
plt.imshow(wf, aspect=0.2, origin='lower')
plt.xlabel('Time steps')
plt.ylabel('Channel #')
```

:::{admonition} Example: Unit waveforms
Use the `channel_structure_intervals` to get information about where each
channel is located.

We need to pass this function a list of channel ids, and it will identify
channels that mark boundaries between identified brain regions.

We can use this information to add some context to our visualization.
:::

```{code-cell} ipython3
# pass in the list of channels from the waveforms data
ecephys_structure_acronyms, intervals = session.channel_structure_intervals(wf.channel_id.values)
print(ecephys_structure_acronyms)
print(intervals)
```

Place tick marks at the interval boundaries, and labels at the interval midpoints.

```{code-cell} ipython3
fig, ax = plt.subplots()
plt.imshow(wf, aspect=0.2, origin='lower')
plt.colorbar(ax=ax)

ax.set_xlabel("time (s)")
ax.set_yticks(intervals)
# construct a list of midpoints by averaging adjacent endpoints
interval_midpoints = [ (aa + bb) / 2 for aa, bb in zip(intervals[:-1], intervals[1:])]
ax.set_yticks(interval_midpoints, minor=True)
ax.set_yticklabels(ecephys_structure_acronyms, minor=True)
plt.tick_params("y", which="major", labelleft=False, length=40)

plt.show()
```

Let's see if this matches the structure information saved in the units table:

```{code-cell} ipython3
session.units.loc[unit, "ecephys_structure_acronym"]
```

:::{admonition} Example: Plot the mean waveform for the peak channel for each unit in the dentate gyrus (DG)
 Start by plotting the mean waveform for the peak channel for the unit we just looked at.
Then do this for all the units in DG, making a heatmap of these waveforms
:::

Find the peak channel for this unit, and plot the mean waveform for just that channel


```{code-cell} ipython3
channel_id = session.units.loc[unit, 'peak_channel_id']
print(channel_id)
```

```{code-cell} ipython3
plt.plot(wf.loc[{"channel_id": channel_id}])
```

```{code-cell} ipython3
fig, ax = plt.subplots()

th_unit_ids = good_units[good_units.ecephys_structure_acronym=="DG"].index.values

peak_waveforms = []

for unit_id in th_unit_ids:

    peak_ch = good_units.loc[unit_id, "peak_channel_id"]
    unit_mean_waveforms = session.mean_waveforms[unit_id]

    peak_waveforms.append(unit_mean_waveforms.loc[{"channel_id": peak_ch}])


time_domain = unit_mean_waveforms["time"]

peak_waveforms = np.array(peak_waveforms)
plt.pcolormesh(peak_waveforms)
```
