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
```{image} ../../resources/cropped-SummerWorkshop_Header.png
:name: workshop-header
```

# Brain Observatory - Neuropixels

This notebook will introduce you to the Neuropixel dataset and SDK functions.

```{code-cell} ipython3
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
```

```{code-cell} ipython3
import platform
platstring = platform.platform()

if 'Darwin' in platstring:
    # OS X
    data_root = "/Volumes/Brain2019/"
elif 'Windows'  in platstring:
    # Windows (replace with the drive letter of USB drive)
    data_root = "E:/"
elif ('amzn1' in platstring):
    # then on AWS
    data_root = "/data/"
else:
    # then your own linux platform
    # EDIT location where you mounted hard drive
    # data_root = "/media/$USERNAME/Brain2019/"
    data_root = "/run/media/galen.lynch/Data/SWDB_2023"

manifest_path = os.path.join(data_root, "visual_coding_neuropixels", "manifest.json")
```

The main entry point is the `EcephyProjectCache` class. This class is
responsible for downloading any requested data or metadata as needed and storing
it in well known locations. For this workshop, all of the data has been
preloaded onto the hard drives you have received, and is available on AWS.

We begin by importing the `EcephysProjectCache` class and instantiating it.

`manifest_path` is a path to the manifest file. We will use the manifest file
preloaded onto your Workshop hard drives. Make sure that `drive_path` is set
correctly for your platform. (See the first cell in this notebook.)

```{code-cell} ipython3
from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
from allensdk.brain_observatory.ecephys import ecephys_session

cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
```

## Exploring available sessions of the dataset

:::{admonition} Example: Get information about what's in the Neuropixels dataset

Use the `get_sessions` function from `EcephysProjectCache` to retrieve a
dataframe of all the available sessions. What information does this dataframe
contain?

* How many sessions are there in the dataset?
* What is the average number of units in an experiment? The max number? The minimum?
* What are the different genotypes that were used in these experiments? How many sessions per genotype?
* What are all the brain structures that data has been collected from?
:::

```{code-cell} ipython3
sessions = cache.get_session_table()
```

```{code-cell} ipython3
:tags: [output_scroll]
sessions.head()
```

How many sessions are available?

```{code-cell} ipython3
sessions.shape[0]
```

What's the average number of units in a session? The max? The min?

```{code-cell} ipython3
print(sessions.unit_count.mean())
print(sessions.unit_count.max())
print(sessions.unit_count.min())
```

```{code-cell} ipython3
plt.hist(sessions.unit_count, bins=20);
plt.xlabel("Unit count")
plt.ylabel("# sessions")
```

What are the different genotypes that were used for this dataset? How many
sessions per genotype are available?

```{code-cell} ipython3
sessions.full_genotype.value_counts()
```

What are the different session types? How many sessions per type?

```{code-cell} ipython3
sessions.session_type.value_counts()
```

What are all the structures that data has been collected from?

```{code-cell} ipython3
all_areas = []
for index,row in sessions.iterrows():
    for a in row.ecephys_structure_acronyms:
        if a not in all_areas:
            all_areas.append(a)
```

```{code-cell} ipython3
print(all_areas)
```

To get more information about these structures, visit
[our reference atlas web app](http://atlas.brain-map.org/atlas?atlas=602630314).

How many sessions have data from VISp?

```{code-cell} ipython3
count=0
for index,row in sessions.iterrows():
    if 'VISp' in row.ecephys_structure_acronyms:
        count+=1
print(count)
```

## The session object
The session object contains all the data and metadata for a single experiment
session, including spike times, stimulus information, unit waveforms and derived
metrics, LFP, and the mouse's running speed.

The session object is accessed using `cache.get_session_data(session_id)`

:::{note}
Experiment data is loaded upon initialization of the class. Some data can be
accessed directly as an attribute of the class, others by using 'get' functions.
:::

:::{admonition} Example: Select a session
Let's pick one session to examine in greater detail. Select a
`brain_observatory_1.1` session. Feel free to use other metadata to select one
session and get the session_id (the index).
:::

```{code-cell} ipython3
session_id = sessions[(sessions.unit_count>900)&(sessions.session_type=='brain_observatory_1.1')
                      &(sessions.full_genotype=='wt/wt')].index[0]
print(session_id)
```

Which areas were recorded from in this session?

```{code-cell} ipython3
sessions.ecephys_structure_acronyms[session_id]
```


:::{admonition} Example: Get the data for this session.

Use the `get_session_data` function of the cache to get the session object for
this session. This object contains the data that is stored in the NWB file.
:::


```{code-cell} ipython3
session = cache.get_session_data(session_id)
```

## Units

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

## Stimuli

 A variety of visual stimuli were presented throughout the recording session, and the session object contains detailed information about what stimuli were presented when.

:::{admonition} Example: Stimulus
What stimuli were presented in this session? Find the `stimulus_names` for the session.
:::

```{code-cell} ipython3
session.stimulus_names
```

:::{admonition} Example: Stimulus epochs
These stimuli are interleaved throughout the session. We can use the
`stimulus_epochs` to see when each stimulus type was presented. Then we'll add
this to the activity plot we made above.
:::

```{code-cell} ipython3
stimulus_epochs = session.get_stimulus_epochs()
stimulus_epochs
```

Remake our plot of V1 activity from above, adding this stimulus epoch
information. Shade each stimulus with a unique color. The **plt.axvspan()** is a
useful function for this.

```{code-cell} ipython3
plt.figure(figsize=(20,10))
for i in range(numunits):
    plt.plot(i+(v1_binned[i,:]/30.), color='gray')

colors = ['blue','orange','green','red','yellow','purple','magenta','gray','lightblue']
for c, stim_name in enumerate(session.stimulus_names):
    stim = stimulus_epochs[stimulus_epochs.stimulus_name==stim_name]
    for j in range(len(stim)):
        plt.axvspan(xmin=stim["start_time"].iloc[j], xmax=stim["stop_time"].iloc[j], color=colors[c], alpha=0.1)
```

Before we dig into the stimulus information in more detail, let's find one more piece of session-wide data that's in the dataset. Running speed.

:::{admonition} Example: Get the running speed
Before we dig further into the stimulus information in more detail, let's add
one more piece of session-wide data to our plot. The mouse's running speed.

Get the `running_speed` and its time stamps from the session object. Plot the
speed as a function of time.
:::

```{code-cell} ipython3
plt.plot(session.running_speed.end_time, session.running_speed.velocity)
plt.xlabel("Time (s)")
plt.ylabel("Running speed (cm/s)")
```

Add the running speed to the plot of V1 activity and stimulus epochs.

```{code-cell} ipython3
plt.figure(figsize=(20,10))
for i in range(numunits):
    plt.plot(i+(v1_binned[i,:]/30.), color='gray')

#scale the running speed and offset it on the plot
plt.plot(session.running_speed.end_time, (0.3*session.running_speed.velocity)-10)

colors = ['blue','orange','green','red','yellow','purple','magenta','gray','lightblue']
for c, stim_name in enumerate(session.stimulus_names):
    stim = stimulus_epochs[stimulus_epochs.stimulus_name==stim_name]
    for j in range(len(stim)):
        plt.axvspan(xmin=stim["start_time"].iloc[j], xmax=stim["stop_time"].iloc[j], color=colors[c], alpha=0.1)

plt.ylim(-10,52)
```

:::{admonition} Example: Stimulus presentations
Now let's go back and learn more about the stimulus that was presented. The
session object has a function that returns a table for a given stimulus called
`get_stimulus_table`.

Use this to get the stimulus table for drifting gratings and for natural scenes.
What information do these tables provide? How are they different?
:::

```{code-cell} ipython3
stim_table = session.get_stimulus_table(['drifting_gratings'])
```

```{code-cell} ipython3
:tags: [output_scroll]
stim_table.head()
```

Now get the stimulus table for natural scenes. What is different about these tables?

```{code-cell} ipython3
stim_table_ns = session.get_stimulus_table(['natural_scenes'])
```

```{code-cell} ipython3
:tags: [output_scroll]
stim_table_ns.head()
```

:::{admonition} Example: Drifting gratings stimulus parameters
Use the drifting grating stimulus table to determine what are the unique
parameters for the different stimulus conditions of this stimulus.
:::

```{code-cell} ipython3
stim_table.orientation.unique()
```

```{code-cell} ipython3
stim_table.spatial_frequency.unique()
```

```{code-cell} ipython3
stim_table.temporal_frequency.unique()
```

```{code-cell} ipython3
stim_table.contrast.unique()
```

What do you think the 'null' conditions are?

:::{admonition} Example: Natural scenes stimulus
Use the stimulus table for natural scenes to find all the times when a
particular image is presented during the session, and add it to the plot of
activity in V1. Pick the first image that was presented in this session.
:::


```{code-cell} ipython3
:tags: [output_scroll]
stim_table_ns[stim_table_ns.frame==stim_table_ns.frame.iloc[0]].head()
```

How many times was it presented?

```{code-cell} ipython3
len(stim_table_ns[stim_table_ns.frame==stim_table_ns.frame.iloc[0]])
```

Mark the times when this particular scene was presented on our plot of the activity (without the epochs and running speed).

```{code-cell} ipython3
plt.figure(figsize=(20,10))
for i in range(numunits):
    plt.plot(i+(v1_binned[i,:]/30.), color='gray')

stim_subset = stim_table_ns[stim_table_ns.frame==stim_table_ns.frame.iloc[0]]
for j in range(len(stim_subset)):
    plt.axvspan(xmin=stim_subset.start_time.iloc[j], xmax=stim_subset.stop_time.iloc[j], color='r', alpha=0.5)
plt.xlim(5000,9000)
```

:::{admonition} Example: Stimulus template
 What is this image? The `stimulus template` provides the images and movies that were presented to the mouse. These are only provided for stimuli that are images (natural scenes, natural movies) - parametric stimuli (eg. gratings) do not have templates.
:::

```{code-cell} ipython3
image_num = 96
image_template = cache.get_natural_scene_template(image_num)

plt.imshow(image_template, cmap='gray')
```

:::{admonition} Example: Single trial raster plots for all units
Now that we've seen the pieces of data, we can explore the neural activity in
greater detail. Make a raster plot for a single presentation of the drifting
grating stimulus at orientation = 45 degrees and temporal frequency = 2 Hz.

To start, make a function to make a raster plot of all the units in the experiment.
:::

```{code-cell} ipython3
def plot_raster(spike_times, start, end):
    num_units = len(spike_times)
    ystep = 1 / num_units

    ymin = 0
    ymax = ystep

    for unit_id, unit_spike_times in spike_times.items():
        unit_spike_times = unit_spike_times[np.logical_and(unit_spike_times >= start, unit_spike_times < end)]
        plt.vlines(unit_spike_times, ymin=ymin, ymax=ymax)

        ymin += ystep
        ymax += ystep

```

Find the first presentation of our chosen grating condition.

```{code-cell} ipython3
stim_table = session.get_stimulus_table(['drifting_gratings'])
subset = stim_table[(stim_table.orientation==45)&(stim_table.temporal_frequency==2)]
start = stim_table.start_time.iloc[0]
end = stim_table.stop_time.iloc[0]
```

Use the plot_raster function to plot the response of all units to this trial. Pad the raster plot with half a second before and after the trial, and shade the trial red (with an alpha of 0.1)

```{code-cell} ipython3
plt.figure(figsize=(8,6))
plot_raster(session.spike_times, start-0.5, end+0.5)
plt.axvspan(start, end, color='red', alpha=0.1)
plt.xlabel('Time (sec)', fontsize=16)
plt.ylabel('Units', fontsize=16)
plt.tick_params(axis="y", labelleft=False, left=False)
plt.show()
```

:::{admonition} Example: Single trial raster plots for all units
Use the `unit` dataframe to arrange the neurons in the raster plot according to
their overall firing rate.
:::

```{code-cell} ipython3
:tags: [output_scroll]
session.units.sort_values(by="firing_rate", ascending=False).head()
```

```{code-cell} ipython3
plt.plot(session.units.sort_values(by="firing_rate", ascending=False).firing_rate.values, 'o')
plt.ylabel("Firing rate (Hz)")
plt.xlabel("Unit #")
```

```{code-cell} ipython3
by_fr = session.units.sort_values(by="firing_rate", ascending=False)
spike_times_by_firing_rate = {
    uid: session.spike_times[uid] for uid in by_fr.index.values
}

plt.figure(figsize=(8,6))
plot_raster(spike_times_by_firing_rate, start-0.5, end+0.5)
plt.axvspan(start, end, color='red', alpha=0.1)
plt.ylabel('Units', fontsize=16)
plt.xlabel('Time (sec)', fontsize=16)
plt.tick_params(axis="y", labelleft=False, left=False)
plt.show()
```

## Stimulus responses

 A lot of the analysis of these data will requires comparing responses of
 neurons to different stimulus conditions and presentations. The SDK has
 functions to help access these, sorting the spike data into responses for each
 stimulus presentations and converting from spike times to binned spike counts.
 This spike histogram representation is more useful for many computations, since
 it can be treated as a timeseries and directly averaged across presentations.

The `presentationwise_spike_counts` provides the histograms for specified
stimulus presentation trials for specified units. The function requires
**stimulus_presentation_ids** for the stimulus in question, **unit_ids** for the
relevant units, and **bin_edges** to specify the time bins to count spikes in
(relative to stimulus onset).

The `conditionwise_spike_statistics` creates a summary of specified units
responses to specified stimulus conditions, including the mean spike count,
standard deviation, and standard error of the mean.

:::{admonition} Example: Presentation-wise analysis for drifting gratings
Pick  a specific condition of the drifting grating stimulus and create spike histograms for the units in V1.
Create bins at a 10 ms resolution so we can see dynamics on a fast timescale.
:::


```{code-cell} ipython3
:tags: [output_scroll]
stim_table.head()
```

```{code-cell} ipython3
# specify the time bins in seconds, relative to stimulus onset
time_step = 1/100.
duration = stim_table.duration.iloc[0]
time_domain = np.arange(0, duration+time_step, time_step)
print(time_domain.shape)
```

```{code-cell} ipython3
stim_ids = stim_table[(stim_table.orientation==90)&(stim_table.temporal_frequency==1)].index
print(stim_ids.shape)
```

```{code-cell} ipython3
histograms = session.presentationwise_spike_counts(bin_edges=time_domain,
                                                   stimulus_presentation_ids=stim_ids,
                                                   unit_ids=v1_units.index)
```

What type of object is this? What is its shape?

```{code-cell} ipython3
type(histograms)
```

```{code-cell} ipython3
histograms.shape
```

### Xarray

This has returned a new (to this notebook) data structure, the
`xarray.DataArray`. You can think of this as similar to a 3+D
`pandas.DataFrame`, or as a `numpy.ndarray` with labeled axes and indices. See
the [xarray documentation](http://xarray.pydata.org/en/stable/index.html) for
more information. In the mean time, the salient features are:

* Dimensions : Each axis on each data variable is associated with a named
  dimension. This lets us see unambiguously what the axes of our array mean.
* Coordinates : Arrays of labels for each sample on each dimension.

xarray is nice because it forces code to be explicit about dimensions and
coordinates, improving readability and avoiding bugs. However, you can always
convert to numpy or pandas data structures as follows:

* to pandas: `histograms.to_dataframe()` produces a multiindexed dataframe
* to numpy: `histograms.values` gives you access to the underlying numpy array


:::{admonition} Example: Plot the unit's response
Plot the response of the first unit to all 15 trials.
:::

```{code-cell} ipython3
for i in range(15):
    plt.plot(histograms.time_relative_to_stimulus_onset, i+histograms[i,:,0])
plt.xlabel("Time (s)", fontsize=16)
plt.ylabel("Trials", fontsize=16)
```

:::{admonition} Example: Compute the average response over trials for all units
Plot a heatmap of mean response for all units in V1.
:::

```{code-cell} ipython3
mean_histograms = histograms.mean(dim="stimulus_presentation_id")
```

```{code-cell} ipython3
mean_histograms.coords
```

```{code-cell} ipython3
import xarray.plot as xrplot
xrplot.imshow(darray=mean_histograms, x="time_relative_to_stimulus_onset",
                                      y="unit_id")
```

:::{admonition} Example: Conditionwise analysis
In order to compute a tuning curve that summarizes the responses of a unit to
each stimulus condition of a stimulus, use the `conditionwise_spike_statistics`
to summarize the activity of specific units to the different stimulus
conditions.
:::

```{code-cell} ipython3
stim_ids = stim_table.index.values
```

```{code-cell} ipython3
dg_stats = session.conditionwise_spike_statistics(stimulus_presentation_ids=stim_ids, unit_ids=v1_units.index)
```

What type of object is this? What is its shape?

```{code-cell} ipython3
type(dg_stats)
```

```{code-cell} ipython3
dg_stats.shape
```

What are its columns?

```{code-cell} ipython3
dg_stats.columns
```

Can you explain the first dimension?

```{code-cell} ipython3
:tags: [output_scroll]
dg_stats.head()
```

:::{admonition} Example: Merge the conditionwise statistics with stimulus information
In order to link the stimulus responses with the stimulus conditions, merge the
spike_statistics output with the stimulus table using `pd.merge()`.
:::

```{code-cell} ipython3
dg_stats_stim = pd.merge(
    dg_stats.reset_index().set_index(['stimulus_condition_id']),
    session.stimulus_conditions,
    on=['stimulus_condition_id']
).reset_index().set_index(['unit_id', 'stimulus_condition_id'])
```

This dataframe currently has a *multi-index*, meaning that each row is indexed
by the pair of unit_id and stimulus_condition_id, rather than a single
identifier. There are several ways to use this index:

* specify the pair of identifiers as a tuple: `dg_stats_stim.loc[(unit_id, stim_id)]`
* specifying the axis makes it easier to get all rows for one unit: `dg_stats_stim.loc(axis=0)[unit_id, :]`
* or you can use `dg_stats_stim.reset_index()` to move the index to regular columns

```{code-cell} ipython3
:tags: [output_scroll]
dg_stats_stim.head()
```

:::{admonition} Example: Tuning curve
Plot a 2D tuning curve for the first unit, comparing responses across temporal
frequency and orientation.
:::

```{code-cell} ipython3
unit_id = v1_units.index[1]
```

```{code-cell} ipython3
stim_ids = stim_table.index.values
session.get_stimulus_parameter_values(stimulus_presentation_ids=stim_ids, drop_nulls=True)
```

```{code-cell} ipython3

orivals = session.get_stimulus_parameter_values(stimulus_presentation_ids=stim_ids, drop_nulls=True)['orientation']
tfvals = session.get_stimulus_parameter_values(stimulus_presentation_ids=stim_ids, drop_nulls=True)['temporal_frequency']
```

```{code-cell} ipython3
response_mean = np.empty((len(orivals), len(tfvals)))
response_sem = np.empty((len(orivals), len(tfvals)))
for i,ori in enumerate(orivals):
    for j,tf in enumerate(tfvals):
        stim_id = stim_table[(stim_table.orientation==ori)&(stim_table.temporal_frequency==tf)].stimulus_condition_id.iloc[0]
        response_mean[i,j] = dg_stats_stim.loc[(unit_id, stim_id)].spike_mean
        response_sem[i,j] = dg_stats_stim.loc[(unit_id, stim_id)].spike_sem
```

```{code-cell} ipython3
plt.imshow(response_mean)
plt.xlabel("Temporal frequency (Hz)")
plt.ylabel("Direction (deg)")
plt.xticks(range(5), tfvals)
plt.yticks(range(8), orivals)
plt.show()
```

## Local Field Potential (LFP)

The final aspect of a Neuropixels probe recording we will investigate is the local field potential (LFP). An LFP signal is a direct recordings of extracellular voltage from which individual spike contributions have been removed by low-pass filtering. The remaining signal reflects the population activity of a large number of cells in the vicinity of the probe, primarily through the electrical field effects of synaptic currents (along with other trans-membrane currents).


LFP can be especially informative for understanding rhythmic activity or oscillations in neural circuits, which can be identified by some simple time-series analysis of the LFP signals.

:::{admonition} Example: Accessing LFP data
We'll start by loading the LFP data from one of the probes in our session, using the `get_lfp` function.

We need to provide this function with a probe id, which we can pull out of the `session.probes` table.

(Note that the "id" column is the index of the dataframe, and thus must be accessed differently than other columns.)
:::

```{code-cell} ipython3
probe_id = session.probes.index[0]
lfp = session.get_lfp(probe_id)
print(lfp)
```

:::{admonition} Example: Plot the LFP data array
To visualize this data, we'll first use the built-in xarray plotting to generate
a quick plot. This is too much data to plot all at once, so we select a subset
first. Just as in pandas, we use the `loc` property, but since xarray has named
dimensions, we can specify our selections by name rather than by order, using a
dict.

We'll also add the structure boundaries to this plot, as we did with unit waveforms.
:::

```{code-cell} ipython3
fig, ax = plt.subplots()
lfp_plot = lfp.loc[dict(time=slice(5,20))]
x, y = lfp_plot.time, range(len(lfp_plot.channel))
plt.pcolormesh(x, y, lfp_plot.values.T)
plt.colorbar(ax=ax)

ax.set_xlabel("time (s)")

# include the structure data
ecephys_structure_acronyms, intervals = session.channel_structure_intervals(lfp.channel.values)
ax.set_yticks(intervals)
interval_midpoints = [ (aa + bb) / 2 for aa, bb in zip(intervals[:-1], intervals[1:])]
ax.set_yticks(interval_midpoints, minor=True)
ax.set_yticklabels(ecephys_structure_acronyms, minor=True)
plt.tick_params("y", which="major", labelleft=False, length=40)
plt.show()
```

:::{admonition} Example: Plot and filter single-channel LFP timeseries
Let's look at the low frequency potentials (LFP) for these data.
:::

We'll start by plotting the timeseries of a single channel.

```{code-cell} ipython3
channel = lfp.channel[0]
lfp_subset = lfp.loc[dict(channel=channel, time=slice(5,20))]

# you might then want to clear the full LFP from memory if not using it
# lfp = None

plt.figure(figsize=(12,3))
lfp_subset.plot()
plt.show()
```

We might also want to visualize a specific frequency band by filtering. To do this we'll want to convert our data into standard numpy arrays for easier processing using the DataArray object's `values` property.

```{code-cell} ipython3
t = lfp_subset.time.values
v = lfp_subset.values
```

```{code-cell} ipython3
import scipy.signal
freq_window = (4, 10)
filt_order = 3
fs = 1/(t[1]-t[0])
b, a = scipy.signal.butter(filt_order, freq_window, btype='bandpass', fs=fs)
v_alpha = scipy.signal.lfilter(b, a, v)

plt.figure(figsize=(12,3))
plt.plot(t, v)
plt.plot(t, v_alpha,'k')
```

:::{admonition} Example: LFP Power spectral density (PSD)
Next we're going to analyze some spectral properties of this signal using the
`scipy.signal` library. "Spectral" refers to decomposing a signal into a sum of
simpler components identified by their frequencies. The set of frequencies of
the components forms a *spectrum* that tells us about the complete signal. You
can see a full list of spectral analysis functions in scipy here:
https://docs.scipy.org/doc/scipy/reference/signal.html#spectral-analysis
:::

We first import the package, and inspect the `periodogram` function, which estimates the size of the different frequency components of the signal.

```{code-cell} ipython3
:tags: ["hide-output"]
import scipy.signal
help(scipy.signal.periodogram)
```

There are a number of options that we won't go into here for refining the analysis. The one piece of information we do need is `fs`, the sampling frequency. If we used the default value `fs=1.0` our results would not match the true frequencies of the signal.

```{code-cell} ipython3
fs = 1/(t[1]-t[0])

f, psd = scipy.signal.periodogram(v, fs)
```

We'll plot the power spectrum on a semilog plot, since power can vary over many orders of magnitude across frequencies.

```{code-cell} ipython3
plt.figure(figsize=(6,3))
plt.semilogy(f,psd,'k')
plt.xlim((0,100))
plt.yticks(size=15)
plt.xticks(size=15)
plt.ylabel('Power ($uV^{2}/Hz$)',size=20)
plt.xlabel('Frequency (Hz)',size=20)
plt.show()
```

We see that this representation of the power spectrum is extremely noisy. Luckily, many people have come up with solutions to this problem. Scipy includes a function for Welch's method, which averages out noise by computing many estimates of the power spectrum from overlapping windows of the data. You can find some more references for this approach in the Scipy documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html#scipy.signal.welch

```{code-cell} ipython3
f, psd = scipy.signal.welch(v, fs, nperseg=1000)

plt.figure(figsize=(6,3))
plt.semilogy(f,psd,'k')
plt.xlim((0,100))
plt.yticks(size=15)
plt.xticks(size=15)
plt.ylabel('Power ($uV^{2}/Hz$)',size=20)
plt.xlabel('Frequency (Hz)',size=20)
plt.show()
```

:::{admonition} Example: Calculate and plot the time-frequency profile ("spectrogram")
We might also be interested in how the frequency content of the signal varies
over time. In a neural context, power in different frequency bands is often
linked to specific types of processing, so we might explore whether changes in
the spectrum coincide with specific behaviors or stimuli.

The *spectrogram* is essentially an estimate of the power spectrum computed in a
sliding time window, producing a 2D representation of the signal power across
frequency and time.
:::

```{code-cell} ipython3
f, t_spec, spec = scipy.signal.spectrogram(v, fs=fs, window='hanning',
                            nperseg=1000, noverlap=1000-1, mode='psd')
# Scipy assumes our signal starts at time=0, so we need to provide the offset
t_spec = t_spec + t[0]
```

We'll use the matplotlib `pcolormesh` function to visualize this data as an image. We can pass this function x and y coordinates to get the axis labeling right. We also log-transform the power spectrum and restrict to frequencies less than 100 Hz.

```{code-cell} ipython3
fmax = 80
x, y = t_spec, f[f<fmax]
plot_data = np.log10(spec[f<fmax])
```

We'll plot the spectrum together with the raw signal in subplots. Note that we explicitly set the x-axis limits to align the plots. (Alternatively, it's possible to directly couple the limits of different subplots.)

```{code-cell} ipython3
from matplotlib import cm
plt.figure(figsize=(10,4))

plt.subplot(2,1,1)
plt.pcolormesh(x, y, plot_data, cmap=cm.jet)
window = [5,20]
plt.xlim(window)
plt.ylabel('Frequency (Hz)')

plt.subplot(2,1,2)
plt.plot(t, v, 'k')
plt.xlim(window)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (a.u.)')
plt.show()
```

## Other resources

These data and the AllenSDK have been documented many times in many places. Here
are some other resource:

* [brain-map.org](https://portal.brain-map.org/explore/circuits/visual-coding-neuropixels)
  * Of particular note is the
  [cheat sheet](https://brainmapportal-live-4cc80a57cd6e400d854-f7fdcae.divio-media.net/filer_public/0f/5d/0f5d22c9-f8f6-428c-9f7a-2983631e72b4/neuropixels_cheat_sheet_nov_2019.pdf)
    from brain-map.org
* [Allen SDK documentation](https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html)
  * The [API documentation of Allen SDK](https://allensdk.readthedocs.io/en/latest/allensdk.brain_observatory.ecephys.html )
* [Notebooks from previous SWDBs](https://github.com/AllenInstitute/swdb_2022/blob/main/DynamicBrain/Visual_Coding_materials/Visual_Coding_Neuropixels_SWDB_2019.ipynb)
