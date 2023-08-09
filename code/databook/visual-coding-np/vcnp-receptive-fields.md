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

# Stimuli

 A variety of visual stimuli were presented throughout the recording session, and the session object contains detailed information about what stimuli were presented when.

:::{admonition} Example: Stimulus
What stimuli were presented in this session? Find the `stimulus_names` for the session.
:::

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

```

```{code-cell} ipython3
spike_times = session.spike_times
max_spike_time = np.fromiter(map(max, spike_times.values()), dtype=np.double).max()
numbins = int(np.ceil(max_spike_time))
v1_units = session.units[session.units.ecephys_structure_acronym=='VISp']
numunits = min(len(v1_units), 50)
v1_binned = np.empty((numunits, numbins))
for i in range(numunits):
    unit_id = v1_units.index[i]
    spikes = spike_times[unit_id]
    for j in range(numbins):
        v1_binned[i,j] = len(spikes[(spikes>j)&(spikes<j+1)])
```

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
