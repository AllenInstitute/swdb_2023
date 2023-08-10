---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Local field potential (LFP)

The final aspect of a Neuropixels probe recording we will investigate is the
local field potential (LFP). An LFP signal is a direct recordings of
extracellular voltage from which individual spike contributions have been
removed by low-pass filtering. The remaining signal reflects the population
activity of a large number of cells in the vicinity of the probe, primarily
through the electrical field effects of synaptic currents (along with other
trans-membrane currents).

LFP can be especially informative for understanding rhythmic activity or
oscillations in neural circuits, which can be identified by some simple
time-series analysis of the LFP signals.

## Tutorial overview

This Jupyter notebook will demonstrate how to access and analyze LFP data from
the Neuropixels Visual Coding dataset. LFP, which stands for "local field
potential," contains information about low-frequency (0.1-500 Hz) voltage
fluctations around each recording site. It's complementary to the spiking
activity, and can be analyzed on its own or in conjunction with spikes.

This tutorial will cover the following topics:

* {ref}`content:references:probe-selection`
* {ref}`content:references:loading-lfp`
* {ref}`content:references:stim-alignment`
* {ref}`content:references:unit-alignment`
* {ref}`content:references:filtering`
* {ref}`content:references:csd`

This tutorial assumes you've already created a data cache, or are working with
the files on AWS. If you haven't reached that step yet, we recommend going
through the {doc}`data access tutorial<vcnp-data-access>` first.

Functions related to analyzing spike data will be covered in other tutorials.
For a full list of available tutorials, see the {doc}`./vcnp` page.

Let's start by creating an `EcephysProjectCache` object, and pointing it to a new or existing manifest file:

:::{admonition} Example: Accessing LFP data
We'll start by loading the LFP data from one of the probes in our session, using the `get_lfp` function.

We need to provide this function with a probe id, which we can pull out of the `session.probes` table.

(Note that the "id" column is the index of the dataframe, and thus must be accessed differently than other columns.)
:::

First we access the data for an example session.

```{code-cell} ipython3
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
```

If you're not sure what a manifest file is or where to put it, please check out the
{doc}`data access tutorial<vcnp-data-access>` before going further.

```{code-cell} ipython3
# Example cache directory path, it determines where downloaded data will be stored
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
```

```{code-cell} ipython3
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
session_id = 715093703 # An example session id
session = cache.get_session_data(session_id)
```

(content:references:probe-selection)=
## Selecting probes to analyze

The `session` object contains all of the spike data for one recording session,
as well as information about the stimulus, mouse behavior, and probes. To
prevent the underlying NWB file from becoming too large, the LFP data is stored
separately, on a probe-by-probe basis. Before loading the LFP, let's take a look
at the probes that are available for this session.

```{code-cell} ipython3
session.probes
```

There are six probes available, and all of them have LFP data. Note that there
is a small subset of probes across the entire dataset that only have spike data,
due to high levels of electrical noise contamining the LFP band. To see which
sessions are missing LFP data, you can check the `probes` table from the
`EcephysProjectCache`:

```{code-cell} ipython3
probes = cache.get_probes()

print('Fraction of probes with LFP: ' + str(np.around( np.sum(probes.has_lfp_data) / len(probes), 3) ) )
print(' ')
print('Sessions with missing LFP files: ' + str(list(probes[probes.has_lfp_data == False].ecephys_session_id.unique())))
```

Returning to the current session, let's get some information about which brain
regions each probe is recording from before we select LFP data to look at in
more detail.

Each probe has a unique ID, but the "description" of each probe is assigned
based on its location on the recording rig. The Allen Institute Neuropixels rigs
have six slot for probes, which are named A, B, C, D, E, and F. The probes are
arranged in a ring centered on visual cortex. Probe A is in the anterior/medial
position, and the letters go clockwise around the ring.

To visualize what this looks like, we can access the spatial information in this
session's `channels` table:

```{code-cell} ipython3
session.channels.keys()
```

As you can see, the `channels` table mainly contains columns related to the
physical locations, either relative to the probe shank
(`probe_vertical_position` and `probe_horizontal_position`), or relative to the
Allen Common Coordinate Framework (`anterior_posterior_ccf_coordinate`,
`dorsal_ventral_ccf_coordinate`, and `left_right_ccf_coordinate`). Let's use a
combination of these to visualize the locations of the probes in this recording.

```{code-cell} ipython3
plt.rcParams.update({'font.size': 14})

x_coords = session.channels.left_right_ccf_coordinate
y_coords = session.channels.anterior_posterior_ccf_coordinate
color = session.channels.probe_vertical_position

f, ax = plt.subplots(figsize=(8,8))
sc = ax.scatter(-x_coords[x_coords > 0], -y_coords[x_coords > 0], c=color[x_coords > 0], cmap='inferno')
cb = plt.colorbar(sc)
_ = cb.ax.set_ylabel('<<  ventral    ---    dorsal  >>')
_ = ax.set_xlabel('<<  lateral    ---    medial  >>')
_ = ax.set_ylabel('<<  posterior    ---    anterior  >>')
```

This is a top-down view of the locations of each channel, with the color
corresponding to distance along the probe axis (darker = deeper in the brain). A
few things to note about this plot:

* There are only 5 probes visible, even though there were 6 probes in the
  recording. This is because one of the probes was not visible in the optical
  projection tomography volume we use to identify the recording location. If
  this occurs, the probe will be assigned a 3D CCF coordinate of `[-1, -1, -1]`,
  and only cortical units will be given an `ecephys_structure_acronym`.
* The probe trajectories are curved, as a result of warping to the CCF template
  brain. The trajectories are straight in the original brain volume.
* Some of the probes appear longer than others. This may be due to the viewing
  angle (in this plot, the more lateral probes are viewed more perpendicular to
  the insertion axis), or the fact that probes may be inserted to different
  depths.

To figure out which probe is missing, we can check the `probes` table for this session:

```{code-cell} ipython3
session.probes.loc[np.unique(session.channels.probe_id.values[x_coords > 0])].description.values
```

It looks like `probeB` was not registered to the CCF. That means that `probeA`
is in the upper right, `probeC` is in the lower right, and `D`, `E`, and `F` go
clockwise from there. It's helpful to keep these descriptions in mind, because
probes with the same descriptions enter the brain at roughly the same angle
across experiments. Although the precise target point for each probe depends on
the retinotopic map for each mouse, the overall rig geometry remains the same
across sessions.

Let's look at the structures each of these probes passes through:

```{code-cell} ipython3
{session.probes.loc[probe_id].description :
     list(session.channels[session.channels.probe_id == probe_id].ecephys_structure_acronym.unique())
     for probe_id in session.probes.index.values}
```

In general, probes tend to be inserted through cortex (`VIS` structures), into
to hippocampus (`CA1`, `CA3`, `DG`), and down into the thalamus or midbrain. If
there's no CCF registration available (e.g., for `probeB` in this example),
subcortical structures are marked as `grey`.

(content:references:loading-lfp)=
## Loading LFP data

Now that we've seen a general overview of how the probes are oriented and what structures they pass through, let's choose one and load its associated LFP data:

```{code-cell} ipython3
probe_id = session.probes[session.probes.description == 'probeE'].index.values[0]

lfp = session.get_lfp(probe_id)
```

If you haven't tried to access this data previously, you'll have to wait while
the LFP NWB file downloads. Even if you already have the data stored locally, it
may still take a minute to load, since the LFP data is quite large.

Once the data is loaded, we can take a closer look at the `lfp` object:

```{code-cell} ipython3
lfp
```

The LFP data is stored as an
[xarray.DataArray](http://xarray.pydata.org/en/stable/) object, with coordinates
of `time` and `channel`. The xarray library simplifies the process of working
with N-dimensional data arrays, by keeping track of the meaning of each axis. If
this is your first time encountering xarrays, we strongly recommend reading
through the
[documentation](http://xarray.pydata.org/en/stable/quick-overview.html) before
going further. Getting used to xarrays can be frustrating, especially when they
don't behave like numpy arrays. But they are designed to prevent common mistakes
when analyzing multidimensional arrays, so they are well worth learning more
about. Plus, the syntax is modeled on that of the
[pandas](https://pandas.pydata.org/) library, so if you're familiar with that
you already have a head start.

The print-out above already tells us a lot about what the `lfp` object contains.
It stores an array with around 12 million points along the `time` axis and 95
points along the `channel` axis. The `time` axis ranges from 13.5 to around 9600
seconds, while the `channel` axis ranges from 850258492 to 850259244 (these are
the unique IDs for each channel).

Let's use the `DataArray.sel()` method to select a slice through this array
between 100 and 101 seconds:

```{code-cell} ipython3
lfp_slice = lfp.sel(time=slice(100,101))

lfp_slice
```

We see that this new DataArray is smaller than before; it contains the same
number of channels, but only 1250 samples, due to the LFP sample rate of ~1250
Hz.

Let's plot the data for one of the channels:

```{code-cell} ipython3
plt.figure(figsize=(10,2))
_ = plt.plot(lfp_slice.time, lfp_slice.sel(channel=lfp_slice.channel[50]))
plt.xlabel('Time (s)')
plt.ylabel('LFP (V)')
```

Alternatively, we can visualize this slice  of data using matplotlib's `imshow` method:

```{code-cell} ipython3
f, ax = plt.subplots(figsize=(8,8))
im = ax.imshow(lfp_slice.T,aspect='auto',origin='lower',vmin=-1e-3, vmax=1e-3)
cb = plt.colorbar(im, fraction=0.036, pad=0.04)
cb.ax.set_ylabel('LFP (V)')
_ = ax.set_xlabel('Sample number')
_ = ax.set_ylabel('Channel index')
```

Note that we've transposed the original array to place the time dimension along
the x-axis. We've also configured the plot so that the origin of the array is in
the lower-left, so that that channels closer to the probe tip are lower in the
image.

A few things to note about this plot:

* The units of the LFP are volts, so the color scale ranges from -1 to
* Even though there are 384 channels on the Neuropixels probe, there are only 95
  channels in this plot. That's because only every 4th channel is included in
  the NWB file (resulting in 40 micron vertical spacing). In addition, the
  reference channels and channels far outside the brain have been removed.
* The top of the plot is relatively flat. This corresponds to channels that are
  outside the brain. The LFP channels are originally referenced to a ground wire
  embedded in the ACSF/agarose mixture about cortex. Before NWB packaging, the
  LFP data is digitally referenced to the channels outside the brain, to remove
  noise that's shared across the whole probe.
* There's a large increase in LFP power toward the middle of the probe, which
  corresponds to channels in hippocampus.

+++

Let's do some additional data selection to look at just the hippocampal channels
from this recording.

```{code-cell} ipython3
channel_ids = session.channels[(session.channels.probe_id == probe_id) & \
                 (session.channels.ecephys_structure_acronym.isin(['CA1','CA3','DG']))].index.values

lfp_slice2 = lfp_slice.sel(channel=slice(np.min(channel_ids), np.max(channel_ids)))

plt.figure(figsize=(8,4))
im = plt.imshow(lfp_slice2.T,aspect='auto',origin='lower',vmin=-1e-3, vmax=1e-3)
_ = plt.colorbar(im, fraction=0.036, pad=0.04)
_ = plt.xlabel('Sample number')
_ = plt.ylabel('Channel index')
```

### Suggestions for further analysis

* Can you use supervised learning to train a model to accurately identify brain
  regions based on LFP signals alone? What happens when you use this model to
  classify brain regions in recordings without CCF registration?
(content:references:stim-alignment)=


## Aligning LFP data to a stimulus

In the above example, we selected LFP data based on an arbitrary time span (100
to 101 seconds). For many analyses, however, you'll want to align the data to
the onset of a particular type of stimulus.

The AllenSDK provides a number of convenience functions for aligning spikes to
visual stimuli. We are planning to implement similar functions for LFP data in
the near future. Until then, the steps below will show you how to perform this
alignment.

First, we need to select some stimulus presentations to use:

```{code-cell} ipython3
presentation_table = session.stimulus_presentations[session.stimulus_presentations.stimulus_name == 'flashes']

presentation_times = presentation_table.start_time.values
presentation_ids = presentation_table.index.values
```

Now, we can align the LFP to these presentation times using some xarray "magic":

```{code-cell} ipython3
trial_window = np.arange(-0.5, 0.5, 1/500)
time_selection = np.concatenate([trial_window + t for t in presentation_times])

inds = pd.MultiIndex.from_product((presentation_ids, trial_window),
                                  names=('presentation_id', 'time_from_presentation_onset'))

ds = lfp.sel(time = time_selection, method='nearest').to_dataset(name = 'aligned_lfp')
ds = ds.assign(time=inds).unstack('time')

aligned_lfp = ds['aligned_lfp']
```

`aligned_lfp` is a DataArray with dimensions of channels x trials x time. It's
been downsampled (however *without* proper decimation!) to 500 Hz by changing
the time step in the `trial_window` variable.

Because we're using xarrays, the alignment operation is fast, and doesn't
require any `for` loops! There's a lot going on here, so we recommend referring
to the pandas and xarray documentation if anything is confusing.

Now we can visualize the average LFP, aligned to the trial onset:

```{code-cell} ipython3
f,ax = plt.subplots(figsize=(8,6))
im = ax.imshow(aligned_lfp.mean(dim='presentation_id'), aspect='auto', origin='lower', vmin=-1e-4, vmax=1e-4)
_ = plt.colorbar(im, fraction=0.036, pad=0.04)
_ = plt.xlabel('Sample number')
_ = plt.ylabel('Channel index')
```

Here we see the effect of a 250 ms flash stimulus on the LFP. There are two
large responses in cortex (channel index 60-80), one corresponding to the
stimulus onset (around sample 280), and one corresponding to the stimulus offset
(around sample 400).

Note that the voltage range is an order of magnitude less than it was for the
single-trial LFP, around -100 to

You can use the code sample above to align the LFP to any type of event (e.g.
spike times, running onset, optogenetic stimuli) just by changing the
`trial_window` and `time_selection` variables.


### Suggestions for further analysis

* How do the time delays of stimulus-evoked LFP deflections vary across areas and depths? Are these delays different for different stimulus conditions?

* Are there consistent patterns in the LFP when aligning to the start of running, or the onset of an eye movement?

(content:references:unit-alignment)=
## Aligning LFP data in space to units

The previous section demonstrated how to align the LFP in time. What if we want
to extract the LFP at a particular location in space, corresponding to the
location of a unit we're analyzing?

Let's start by finding a well-isolated, high-firing rate unit in visual cortex
from the probe we're currently working with. For more information about using
quality metrics to assess unit isolation quality, check out
{doc}`this tutorial<vcnp-quality-metrics>`.

Once we've selected a unit of interest, the xarray library makes it easy to find
the associated LFP channel.

```{code-cell} ipython3
units_of_interest = session.units[(session.units.probe_id == probe_id) &
                                  (session.units.ecephys_structure_acronym.str.find('VIS') > -1) &
                                  (session.units.firing_rate > 10) &
                                  (session.units.nn_hit_rate > 0.95)]

len(units_of_interest)
```

There are four units that meet our criteria. Let's choose one and find its associated channel index.

```{code-cell} ipython3
unit_id = units_of_interest.index.values[0]

channel_index = units_of_interest.loc[unit_id].probe_channel_number

channel_index
```

Note that this is the channel index relative to the original probe (out of 384
possible channels), rather than the index of the LFP DataArray.

We can now use the channel index to find the unique channel ID for this unit:

```{code-cell} ipython3
channel_id = session.channels[(session.channels.probe_channel_number == channel_index) &
                              (session.channels.probe_id == probe_id)].index.values[0]

channel_id
```

Using `unit_id` and `channel_id`, we can select the spikes and LFP within an
arbitrary time interval. Note that we need to use `method='nearest'` when
selecting the LFP data channel, since not every electrode is included in the LFP
DataArray.

```{code-cell} ipython3
start_time = 500
end_time = 510

spike_times = session.spike_times[unit_id]

times_in_range = spike_times[(spike_times > start_time) & (spike_times < end_time)]

lfp_data = lfp.sel(time = slice(start_time, end_time))
lfp_data = lfp_data.sel(channel = channel_id, method='nearest')
```

Finally, we can plot the spike times along with the LFP for this interval:

```{code-cell} ipython3
_ = plt.plot(lfp_data.time, lfp_data)
_ = plt.plot(times_in_range, np.ones(times_in_range.shape)*3e-4, '.r')
_ = plt.xlabel('Time (s)')
_ = plt.ylabel('LFP (V)')
```

### Suggestions for further analysis

* What does the spike-triggered LFP look like for different units? Is it possible to classify units based on the properties of the spike-triggered LFP?

* How well can you predict spike rates from the nearby LFP signals? Does this vary across different brain regions?

(content:references:filtering)=
## Filtering and spectral estimation of LFP
We'll start by plotting the timeseries of a single channel, as we did above.

```{code-cell} ipython3
channel = lfp.channel[50]
lfp_subset = lfp.sel(channel=channel, time=slice(15, 30))

plt.figure(figsize=(12,3))
lfp_subset.plot()
plt.show()
```

This signal contains compononts of multiple frequencies. We can isolate a
frequency band of interest by filtering. To do this we'll want to convert our
data into standard numpy arrays for easier processing using the DataArray
object's `values` property.

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

f, ax = plt.subplots(figsize=(12,3))
ax.plot(t, v)
ax.plot(t, v_alpha,'k')
ax.set_xlabel('Time (s)')
ax.set_ylabel('LFP (V)')
```

:::{admonition} Example: LFP Power spectral density (PSD)
Next we're going to analyze some spectral properties of this signal using the
`scipy.signal` library. "Spectral" refers to decomposing a signal into a sum of
simpler components identified by their frequencies. The set of frequencies of
the components forms a *spectrum* that tells us about the complete signal. You
can see a full list of spectral analysis functions in scipy here:
https://docs.scipy.org/doc/scipy/reference/signal.html#spectral-analysis
:::

We first import the package, and inspect the `periodogram` function, which
estimates the size of the different frequency components of the signal.

```{code-cell} ipython3
:tags: [hide-output]

import scipy.signal
help(scipy.signal.periodogram)
```

There are a number of options that we won't go into here for refining the
analysis. The one piece of information we do need is `fs`, the sampling
frequency. If we used the default value `fs=1.0` our results would not match the
true frequencies of the signal.

```{code-cell} ipython3
fs = 1/(t[1]-t[0])

f, psd = scipy.signal.periodogram(v, fs)
```

We'll plot the power spectrum on a semilog plot, since power can vary over many
orders of magnitude across frequencies.

```{code-cell} ipython3
plt.figure(figsize=(6,3))
plt.semilogy(f,psd,'k')
plt.xlim((0,100))
plt.yticks(size=15)
plt.xticks(size=15)
plt.ylabel('Power ($V^{2}/Hz$)')
plt.xlabel('Frequency (Hz)')
plt.show()
```

We see that this representation of the power spectrum is extremely noisy.
Luckily, many people have come up with solutions to this problem. Scipy includes
a function for Welch's method, which averages out noise by computing many
estimates of the power spectrum from overlapping windows of the data. You can
find some more references for this approach in the
[Scipy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html#scipy.signal.welch.). For more powerful spectral estimation techniques, try multitaper.

```{code-cell} ipython3
f, psd = scipy.signal.welch(v, fs, nperseg=1000)

plt.figure(figsize=(6,3))
plt.semilogy(f,psd,'k')
plt.xlim((0,100))
plt.yticks(size=15)
plt.xticks(size=15)
plt.ylabel('Power ($V^{2}/Hz$)')
plt.xlabel('Frequency (Hz)')
plt.show()
```

:::{admonition} Example: Calculate and plot the time-frequency profile ("spectrogram")
We might also be interested in how the frequency content of the signal varies
over time. In a neural context, power in different frequency bands is often
linked to specific types of processing, so we might explore whether changes in
the spectrum coincide with specific behaviors or stimuli.

The *spectrogram* is an estimate of the power spectrum computed in a sliding
time window, producing a 2D representation of the signal power across frequency
and time.
:::

```{code-cell} ipython3
fs
```

```{code-cell} ipython3
:tags: [hide-output]

help(scipy.signal.spectrogram)
```

```{code-cell} ipython3
f, t_spec, spec = scipy.signal.spectrogram(v, fs=fs, window='hann',
                            nperseg=1000, noverlap=1000-1, mode='psd')
# Scipy assumes our signal starts at time=0, so we need to provide the offset
t_spec = t_spec + t[0]
```

We'll use the matplotlib `pcolormesh` function to visualize this data as an
image. We can pass this function x and y coordinates to get the axis labeling
right. We also log-transform the power spectrum and restrict to frequencies less
than 100 Hz.

```{code-cell} ipython3
fmax = 80
x, y = t_spec, f[f<fmax]
plot_data = np.log10(spec[f<fmax])
```

We'll plot the spectrum together with the raw signal in subplots. Note that we
explicitly link the x-axis limits to align the plots.

```{code-cell} ipython3
from matplotlib import cm
f, axs = plt.subplots(2, 1, sharex = True, figsize=(10,4)) # X axes are linked
time_window = [15, 30]

_ = axs[0].pcolormesh(x, y, plot_data)
_ = axs[0].set_ylabel('Frequency (Hz)')

_ = axs[1].plot(t, v, 'k')
_ = axs[1].set_xlim(time_window)
_ = axs[1].set_xlabel('Time (s)')
_ = axs[1].set_ylabel('Voltage (V)')
```

(content:references:csd)=
## Exploring pre-computed current source density plots

LFP data is commonly used to generate current source density (CSD) plots, which
show the location of current sources and sinks along the probe axis. CSD
analysis benefits from high spatial resolution, since it involves taking the
second spatial derivative of the data. Because of Neuropixels dense site
spacing, these probes are optimal for computing the CSD. However, the LFP data
available through the AllenSDK has been spatially downsampled prior to NWB
packaging.

To provide access to a high-resolution CSD plot, we've pre-computed the CSD in
response to a flash stimulus for all probes with LFP.

```{code-cell} ipython3
csd = session.get_current_source_density(probe_id)
csd
```

The `CSD` object is a DataArray with dimensions of channels x time. Note that
the channels are actually "virtual channels," based on interpolated signals
along the central axis of the probe, with 10 micron inter-site spacing.

```{code-cell} ipython3
from scipy.ndimage.filters import gaussian_filter

filtered_csd = gaussian_filter(csd.data, sigma=(5,1))

f, ax = plt.subplots(figsize=(6, 6))

_ = ax.pcolor(csd["time"], csd["vertical_position"], filtered_csd, vmin=-3e4, vmax=3e4)
_ = ax.set_xlabel("time relative to stimulus onset (s)")
_ = ax.set_ylabel("vertical position (um)")
```

This CSD shows a clear stimulus-evoked response in cortex (2600-3500 microns),
with an even earlier response in a subcortical region (700-1200 microns).

We can use the `channels` table to figure out where this signal is coming from:

```{code-cell} ipython3
list(session.channels[(session.channels.probe_id == probe_id) &
                 (session.channels.probe_vertical_position > 700) &
                 (session.channels.probe_vertical_position < 1200)].ecephys_structure_acronym.unique())
```

It looks like this region of the probe is on the border between LGd and LP nuclei in the thalamus.

### Suggestions for further analysis

* How does the cortical CSD vary across visual areas? Are there consistent patterns across all areas?

* Are the locations of sources and sinks correlated with other features of the LFP, such as power in different frequency bands?
