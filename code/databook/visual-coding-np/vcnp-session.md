---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.15.0
kernelspec:
  display_name: allensdk
  language: python
  name: allensdk
---

# Extracellular Electrophysiology Data

At the Allen Institute for Brain Science we carry out in vivo extracellular
electrophysiology (ecephys) experiments in awake animals using high-density
Neuropixels probes. The data from these experiments are organized into
*sessions*, where each session is a distinct continuous recording period. During
a session we collect:

- spike times and characteristics (such as mean waveforms) from up to 6
  neuropixels probes
- local field potentials
- behavioral data, such as running speed and eye position
- visual stimuli which were presented during the session
- cell-type specific optogenetic stimuli that were applied during the session

The AllenSDK contains code for accessing across-session (project-level) metadata
as well as code for accessing detailed within-session data. The standard
workflow is to use project-level tools, such as `EcephysProjectCache` to
identify and access sessions of interest, then delve into those sessions' data
using `EcephysSession`.


## Project-level
The `EcephysProjectCache` class in
`allensdk.brain_observatory.ecephys.ecephys_project_cache` accesses and stores
data pertaining to many sessions. You can use this class to run queries that
span all collected sessions and to download data for individual sessions.
* <a href='#Obtaining-an-EcephysProjectCache'>Obtaining an
  `EcephysProjectCache`</a>
* <a href='#Querying-across-sessions'>Querying sessions</a>
* <a href='#Querying-across-probes'>Querying probes</a>
* <a href='#Querying-across-units'>Querying units</a>
* <a href='#Surveying-metadata'>Surveying metadata</a>


## Session-level
The `EcephysSession` class in
`allensdk.brain_observatory.ecephys.ecephys_session` provides an interface to
all of the data for a single session, aligned to a common clock. This notebook
will show you how to use the `EcephysSession` class to extract these data.
* <a href='#Obtaining-an-EcephysSession'>Obtaining an `EcephysSession`</a>
* <a href='#Stimulus-presentations'>Stimulus information</a>
* <a href='#Spike-data'>Spike data</a>
* <a href='#Spike-histograms'>Spike histograms</a>
* <a href='#Running-speed'>Running speed</a>
* <a href='#Optogenetic-stimulation'>Optogenetic stimulation</a>
* <a href='#Local-field-potential'>Local Field Potential</a>
* <a href='#Current-source-density'>Current source density</a>
* <a href='#Waveforms'>Unitwise mean waveforms</a>
* <a href='#Suggested-exercises'>Suggested exercises</a>
* <a href='#Eye-tracking-ellipse-fits-and-estimated-screen-gaze-location'>Eye
  tracking ellipse fits and estimated screen gaze location</a>

```{code-cell} ipython3

# first we need a bit of import boilerplate
import os

import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
from pathlib import Path
import json
from IPython.display import display
from PIL import Image

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
from allensdk.brain_observatory.ecephys.ecephys_session import (
    EcephysSession,
    removed_unused_stimulus_presentation_columns
)
from allensdk.brain_observatory.ecephys.visualization import plot_mean_waveforms, plot_spike_counts, raster_plot
from allensdk.brain_observatory.visualization import plot_running_speed

# tell pandas to show all columns when we display a DataFrame
pd.set_option("display.max_columns", None)
```



### Obtaining an `EcephysProjectCache`

In order to create an `EcephysProjectCache` object, you need to specify two
things:
1. A remote source for the object to fetch data from. We will instantiate our
   cache using `EcephysProjectCache.from_warehouse()` to point the cache at the
   Allen Institute's public web API.
2. A path to a manifest json, which designates filesystem locations for
   downloaded data. The cache will try to read data from these locations before
   going to download those data from its remote source, preventing repeated
   downloads.

```{code-cell} ipython3
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
resources_dir = Path.cwd().parent / 'resources'
DOWNLOAD_LFP = False
```

```{code-cell} ipython3

# Example cache directory path, it determines where downloaded data will be stored
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
```



### Querying across sessions

Using your `EcephysProjectCache`, you can download a table listing metadata for
all sessions.

```{code-cell} ipython3

cache.get_session_table().head()
```



### Querying across probes

... or for all probes

```{code-cell} ipython3

cache.get_probes().head()
```



### Querying across channels

... or across channels.

```{code-cell} ipython3

cache.get_channels().head()
```



### Querying across units

... as well as for sorted units.

```{code-cell} ipython3

units = cache.get_units()
units.head()
```

```{code-cell} ipython3

# There are quite a few of these
print(units.shape[0])
```



### Surveying metadata

You can answer questions like: "what mouse genotypes were used in this dataset?" using your `EcephysProjectCache`.

```{code-cell} ipython3

print(f"stimulus sets: {cache.get_all_session_types()}")
print(f"genotypes: {cache.get_all_full_genotypes()}")
print(f"structures: {cache.get_structure_acronyms()}")
```



In order to look up a brain structure acronym, you can use our [online atlas viewer](http://atlas.brain-map.org/atlas?atlas=602630314). The AllenSDK additionally supports programmatic access to structure annotations. For more information, see the [reference space](https://allensdk.readthedocs.io/en/latest/reference_space.html) and [mouse connectivity](https://allensdk.readthedocs.io/en/latest/connectivity.html) documentation.



### Obtaining an `EcephysSession`

We package each session's data into a Neurodata Without Borders 2.0 (NWB) file.
Calling `get_session_data` on your `EcephysProjectCache` will download such a
file and return an `EcephysSession` object.

`EcephysSession` objects contain methods and properties that access the data
within an ecephys NWB file and cache it in memory.

```{code-cell} ipython3

session_id = 756029989 # for example
session = cache.get_session_data(session_id)
```

This session object has some important metadata, such as the date and time at
which the recording session started:

```{code-cell} ipython3

print(f"session {session.ecephys_session_id} was acquired in {session.session_start_time}")
```



We'll now jump in to accessing our session's data. If you ever want a complete
documented list of the attributes and methods defined on `EcephysSession`, you
can run `help(EcephysSession)` (or in a jupyter notebook: `EcephysSession?`).



### Sorted units

Units are putative neurons, clustered from raw voltage traces using Kilosort 2.
Each unit is associated with a single *peak channel* on a single probe, though
its spikes might be picked up with some attenuation on multiple nearby channels.
Each unit is assigned a unique integer identifier ("unit_id") which can be used
to look up its spike times and its mean waveform.

The units for a session are recorded in an attribute called, fittingly, `units`.
This is a `pandas.DataFrame` whose index is the unit id and whose columns
contain summary information about the unit, its peak channel, and its associated
probe.

```{code-cell} ipython3

session.units.head()
```



As a `pandas.DataFrame` the units table supports many straightforward filtering
operations:

```{code-cell} ipython3

# how many units have signal to noise ratios that are greater than 4?
print(f'{session.units.shape[0]} units total')
units_with_very_high_snr = session.units[session.units['snr'] > 4]
print(f'{units_with_very_high_snr.shape[0]} units have snr > 4')
```



... as well as some more advanced (and very useful!) operations. For more
information, please see the pandas documentation. The following topics might be
particularly handy:

* [selecting data](http://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html)
* [merging multiple dataframes](http://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html)
* [grouping rows within a dataframe](http://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html)
* [pivot tables](http://pandas.pydata.org/pandas-docs/stable/user_guide/reshaping.html)


### Stimulus presentations

During the course of a session, visual stimuli are presented on a monitor to the subject. We call intervals of time where a specific stimulus is presented (and its parameters held constant!) a *stimulus presentation*.

You can find information about the stimulus presentations that were displayed during a session by accessing the `stimulus_presentations` attribute on your `EcephysSession` object.

```{code-cell} ipython3

session.stimulus_presentations.head()
```



Like the units table, this is a `pandas.DataFrame`. Each row corresponds to a stimulus presentation and lists the time (on the session's master clock, in seconds) when that presentation began and ended as well as the kind of stimulus that was presented (the "stimulus_name" column) and the parameter values that were used for that presentation. Many of these parameter values don't overlap between stimulus classes, so the stimulus_presentations table uses the string `"null"` to indicate an inapplicable parameter. The index is named "stimulus_presentation_id" and many methods on `EcephysSession` use these ids.

Some of the columns bear a bit of explanation:
- stimulus_block : A block consists of multiple presentations of the same stimulus class presented with (probably) different parameter values. If during a session stimuli were presented in the following order:
    - drifting gratings
    - static gratings
    - drifting gratings
    then the blocks for that session would be [0, 1, 2]. The gray period stimulus (just a blank gray screen) never gets a block.
- duration : this is just stop_time - start_time, precalculated for convenience.

What kinds of stimuli were presented during this session? Pandas makes it easy to find out:

```{code-cell} ipython3

session.stimulus_names # just the unique values from the 'stimulus_name' column
```



We can also obtain the `stimulus epochs` - blocks of time for which a particular
kind of stimulus was presented - for this session.

```{code-cell} ipython3

session.get_stimulus_epochs()
```

If you are only interested in a subset of stimuli, you can either filter using
pandas or using the `get_stimulus_table` convience method:

```{code-cell} ipython3

session.get_stimulus_table(['drifting_gratings']).head()
```

We might also want to know what the total set of available parameters is. The
`get_stimulus_parameter_values` method provides a dictionary mapping stimulus
parameters to the set of values that were applied to those parameters:

```{code-cell} ipython3

for key, values in session.get_stimulus_parameter_values().items():
    print(f'{key}: {values}')
```

Each distinct state of the monitor is called a "stimulus condition". Each
presentation in the stimulus presentations table exemplifies such a condition.
This is encoded in its stimulus_condition_id field.

To get the full list of conditions presented in a session, use the stimulus_conditions attribute:

```{code-cell} ipython3

session.stimulus_conditions.head()
```

### Spike data

The `EcephysSession` object holds spike times (in seconds on the session master
clock) for each unit. These are stored in a dictionary, which maps unit ids (the
index values of the units table) to arrays of spike times.

```{code-cell} ipython3

 # grab an arbitrary (though high-snr!) unit (we made units_with_high_snr above)
high_snr_unit_ids = units_with_very_high_snr.index.values
unit_id = high_snr_unit_ids[0]

print(f"{len(session.spike_times[unit_id])} spikes were detected for unit {unit_id} at times:")
session.spike_times[unit_id]
```



You can also obtain spikes tagged with the stimulus presentation during which
they occurred:

```{code-cell} ipython3

# get spike times from the first block of drifting gratings presentations
drifting_gratings_presentation_ids = session.stimulus_presentations.loc[
    (session.stimulus_presentations['stimulus_name'] == 'drifting_gratings')
].index.values

times = session.presentationwise_spike_times(
    stimulus_presentation_ids=drifting_gratings_presentation_ids,
    unit_ids=high_snr_unit_ids
)

times.head()
```



We can make raster plots of these data:

```{code-cell} ipython3

first_drifting_grating_presentation_id = times['stimulus_presentation_id'].values[0]
plot_times = times[times['stimulus_presentation_id'] == first_drifting_grating_presentation_id]

fig = raster_plot(plot_times, title=f'spike raster for stimulus presentation {first_drifting_grating_presentation_id}')
plt.show()

# also print out this presentation
session.stimulus_presentations.loc[first_drifting_grating_presentation_id]
```



We can access summary spike statistics for stimulus conditions and unit

```{code-cell} ipython3

stats = session.conditionwise_spike_statistics(
    stimulus_presentation_ids=drifting_gratings_presentation_ids,
    unit_ids=high_snr_unit_ids
)

# display the parameters associated with each condition
stats = pd.merge(stats, session.stimulus_conditions, left_on="stimulus_condition_id", right_index=True)

stats.head()
```

Using these data, we can ask for each unit: which stimulus condition evoked the
most activity on average?

```{code-cell} ipython3

with_repeats = stats[stats["stimulus_presentation_count"] >= 5]

highest_mean_rate = lambda df: df.loc[df['spike_mean'].idxmax()]
max_rate_conditions = with_repeats.groupby('unit_id').apply(highest_mean_rate)
max_rate_conditions.head()
```



### Spike histograms

It is commonly useful to compare spike data from across units and stimulus
presentations, all relative to the onset of a stimulus presentation. We can do
this using the `presentationwise_spike_counts` method.

```{code-cell} ipython3

# We're going to build an array of spike counts surrounding stimulus presentation onset
# To do that, we will need to specify some bins (in seconds, relative to stimulus onset)
time_bin_edges = np.linspace(-0.01, 0.4, 200)

# look at responses to the flash stimulus
flash_250_ms_stimulus_presentation_ids = session.stimulus_presentations[
    session.stimulus_presentations['stimulus_name'] == 'flashes'
].index.values

# and get a set of units with only decent snr
decent_snr_unit_ids = session.units[
    session.units['snr'] >= 1.5
].index.values

spike_counts_da = session.presentationwise_spike_counts(
    bin_edges=time_bin_edges,
    stimulus_presentation_ids=flash_250_ms_stimulus_presentation_ids,
    unit_ids=decent_snr_unit_ids
)
spike_counts_da
```

This has returned a new (to this notebook) data structure, the
`xarray.DataArray`. You can think of this as similar to a 3+D
`pandas.DataFrame`, or as a `numpy.ndarray` with labeled axes and indices. See
the [xarray documentation](http://xarray.pydata.org/en/stable/index.html) for
more information. In the mean time, the salient features are:

- Dimensions : Each axis on each data variable is associated with a named
  dimension. This lets us see unambiguously what the axes of our array mean.
- Coordinates : Arrays of labels for each sample on each dimension.

xarray is nice because it forces code to be explicit about dimensions and
coordinates, improving readability and avoiding bugs. However, you can always
convert to numpy or pandas data structures as follows:
- to pandas: `spike_counts_ds.to_dataframe()` produces a multiindexed dataframe
- to numpy: `spike_counts_ds.values` gives you access to the underlying numpy array

We can now plot spike counts for a particular presentation:

```{code-cell} ipython3

presentation_id = 3796 # chosen arbitrarily
plot_spike_counts(
    spike_counts_da.loc[{'stimulus_presentation_id': presentation_id}],
    spike_counts_da['time_relative_to_stimulus_onset'],
    'spike count',
    f'unitwise spike counts on presentation {presentation_id}'
)
plt.show()
```

We can also average across all presentations, adding a new data array to the
dataset. Notice that this one no longer has a stimulus_presentation_id
dimension, as we have collapsed it by averaging.

```{code-cell} ipython3

mean_spike_counts = spike_counts_da.mean(dim='stimulus_presentation_id')
mean_spike_counts
```

... and plot the mean spike counts

```{code-cell} ipython3

plot_spike_counts(
    mean_spike_counts,
    mean_spike_counts['time_relative_to_stimulus_onset'],
    'mean spike count',
    'mean spike counts on flash_250_ms presentations'
)
plt.show()
```



### Waveforms

We store precomputed mean waveforms for each unit in the `mean_waveforms`
attribute on the `EcephysSession` object. This is a dictionary which maps unit
ids to xarray
[DataArrays](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html).
These have `channel` and `time` (seconds, aligned to the detected event times)
dimensions. The data values are in microvolts, as measured at the recording
site.

```{code-cell} ipython3

units_of_interest = high_snr_unit_ids[:35]

waveforms = {uid: session.mean_waveforms[uid] for uid in units_of_interest}
peak_channels = {uid: session.units.loc[uid, 'peak_channel_id'] for uid in units_of_interest}

# plot the mean waveform on each unit's peak channel/
plot_mean_waveforms(waveforms, units_of_interest, peak_channels)
plt.show()
```



Since neuropixels probes are densely populated with channels, spikes are
typically detected on several channels. We can see this by plotting mean
waveforms on channels surrounding a unit's peak channel:

```{code-cell} ipython3

uid = units_of_interest[12]
unit_waveforms = waveforms[uid]
peak_channel = peak_channels[uid]
peak_channel_idx = np.where(unit_waveforms["channel_id"] == peak_channel)[0][0]

ch_min = max(peak_channel_idx - 10, 0)
ch_max = min(peak_channel_idx + 10, len(unit_waveforms["channel_id"]) - 1)
surrounding_channels = unit_waveforms["channel_id"][np.arange(ch_min, ch_max, 2)]

fig, ax = plt.subplots()
ax.imshow(unit_waveforms.loc[{"channel_id": surrounding_channels}])

ax.yaxis.set_major_locator(plt.NullLocator())
ax.set_ylabel("channel", fontsize=16)

ax.set_xticks(np.arange(0, len(unit_waveforms['time']), 20))
ax.set_xticklabels([f'{float(ii):1.4f}' for ii in unit_waveforms['time'][::20]], rotation=45)
ax.set_xlabel("time (s)", fontsize=16)

plt.show()
```



### Running speed

We can obtain the velocity at which the experimental subject ran as a function
of time by accessing the `running_speed` attribute. This returns a pandas
dataframe whose rows are intervals of time (defined by "start_time" and
"end_time" columns), and whose "velocity" column contains mean running speeds
within those intervals.

Here we'll plot the running speed trace for an arbitrary chunk of time.

```{code-cell} ipython3

running_speed_midpoints = session.running_speed["start_time"] + \
    (session.running_speed["end_time"] - session.running_speed["start_time"]) / 2
plot_running_speed(
    running_speed_midpoints,
    session.running_speed["velocity"],
    start_index=5000,
    stop_index=5100
)
plt.show()
```

### Optogenetic stimulation

```{code-cell} ipython3

session.optogenetic_stimulation_epochs
```

### Eye tracking ellipse fits and estimated screen gaze location

Ecephys sessions may contain eye tracking data in the form of ellipse fits and
estimated screen gaze location. Let's look at the ellipse fits first:

```{code-cell} ipython3

pupil_data = session.get_pupil_data()
pupil_data
```

This particular session has eye tracking data, let's try plotting the ellipse
fits over time.

```{code-cell} ipython3

%%capture
from matplotlib import animation
from matplotlib.patches import Ellipse

def plot_animated_ellipse_fits(pupil_data: pd.DataFrame, start_frame: int, end_frame: int):

    start_frame = 0 if (start_frame < 0) else start_frame
    end_frame = len(pupil_data) if (end_frame > len(pupil_data)) else end_frame

    frame_times = pupil_data.index.values[start_frame:end_frame]
    interval = np.average(np.diff(frame_times)) * 1000

    fig = plt.figure()
    ax = plt.axes(xlim=(0, 480), ylim=(0, 480))

    cr_ellipse = Ellipse((0, 0), width=0.0, height=0.0, angle=0, color='white')
    pupil_ellipse = Ellipse((0, 0), width=0.0, height=0.0, angle=0, color='black')
    eye_ellipse = Ellipse((0, 0), width=0.0, height=0.0, angle=0, color='grey')

    ax.add_patch(eye_ellipse)
    ax.add_patch(pupil_ellipse)
    ax.add_patch(cr_ellipse)

    def update_ellipse(ellipse_patch, ellipse_frame_vals: pd.DataFrame, prefix: str):
        ellipse_patch.center = tuple(ellipse_frame_vals[[f"{prefix}_center_x", f"{prefix}_center_y"]].values)
        ellipse_patch.width = ellipse_frame_vals[f"{prefix}_width"]
        ellipse_patch.height = ellipse_frame_vals[f"{prefix}_height"]
        ellipse_patch.angle = np.degrees(ellipse_frame_vals[f"{prefix}_phi"])

    def init():
        return [cr_ellipse, pupil_ellipse, eye_ellipse]

    def animate(i):
        ellipse_frame_vals = pupil_data.iloc[i]

        update_ellipse(cr_ellipse, ellipse_frame_vals, prefix="corneal_reflection")
        update_ellipse(pupil_ellipse, ellipse_frame_vals, prefix="pupil")
        update_ellipse(eye_ellipse, ellipse_frame_vals, prefix="eye")

        return [cr_ellipse, pupil_ellipse, eye_ellipse]

    return animation.FuncAnimation(fig, animate, init_func=init, interval=interval, frames=range(start_frame, end_frame), blit=True)

anim = plot_animated_ellipse_fits(pupil_data, 100, 600)
```

```{code-cell} ipython3

from IPython.display import HTML

HTML(anim.to_jshtml())
```

Using the above ellipse fits and location/orientation information about the
experimental rigs, it is possible to calculate additional statistics such as
pupil size or estimate a gaze location on screen at a given time. Due to the
degrees of freedom in some rig components, gaze estimates have no accuracy
guarantee. For additional information about the gaze mapping estimation process
please refer to:
https://github.com/AllenInstitute/AllenSDK/tree/master/allensdk/brain_observatory/gaze_mapping

```{code-cell} ipython3

gaze_data = session.get_screen_gaze_data()
gaze_data
```

```{code-cell} ipython3

ax = gaze_data[["raw_pupil_area"]].plot()
_ = ax.set_ylabel("Area cm^2")
```

### Local Field Potential

We record local field potential on a subset of channels at 2500 Hz. Even
subsampled and compressed, these data are quite large, so we store them
seperately for each probe.

```{code-cell} ipython3

# list the probes recorded from in this session
session.probes.head()
```

```{code-cell} ipython3

# load up the lfp from one of the probes. This returns an xarray dataarray

probe_id = session.probes.index.values[0]

if DOWNLOAD_LFP:
    lfp = session.get_lfp(probe_id)
    lfp
```

We can figure out where each LFP channel is located in the brain

```{code-cell} ipython3

if DOWNLOAD_LFP:
    # now use a utility to associate intervals of /rows with structures
    structure_acronyms, intervals = session.channel_structure_intervals(lfp["channel"])
    interval_midpoints = [aa + (bb - aa) / 2 for aa, bb in zip(intervals[:-1], intervals[1:])]
else:
    with open(Path(resources_dir) / 'ecephys_session' / 'structure_acronyms.json') as f:
        structure_acronyms = json.load(f)
        structure_acronyms = np.array(structure_acronyms)

    with open(Path(resources_dir) / 'ecephys_session' / 'intervals.json') as f:
        intervals = json.load(f)
        intervals = np.array(structure_acronyms)
print(structure_acronyms)
print(intervals)
```

```{code-cell} ipython3

if DOWNLOAD_LFP:
    window = np.where(np.logical_and(lfp["time"] < 5.0, lfp["time"] >= 4.0))[0]

    fig, ax = plt.subplots()
    ax.pcolormesh(lfp[{"time": window}].T)

    ax.set_yticks(intervals)
    ax.set_yticks(interval_midpoints, minor=True)
    ax.set_yticklabels(structure_acronyms, minor=True)
    plt.tick_params("y", which="major", labelleft=False, length=40)

    num_time_labels = 8
    time_label_indices = np.around(np.linspace(1, len(window), num_time_labels)).astype(int) - 1
    time_labels = [ f"{val:1.3}" for val in lfp["time"].values[window][time_label_indices]]
    ax.set_xticks(time_label_indices + 0.5)
    ax.set_xticklabels(time_labels)
    ax.set_xlabel("time (s)", fontsize=20)

    plt.show()
else:
    lfp_plot = Image.open(Path(resources_dir) /
                          'ecephys_session' /
                          'lfp_plot.png')
    display(lfp_plot)
```



### Current source density

We precompute current source density for each probe.

```{code-cell} ipython3
if DOWNLOAD_LFP:
    csd = session.get_current_source_density(probe_id)
    csd
```

```{code-cell} ipython3

if DOWNLOAD_LFP:
    filtered_csd = gaussian_filter(csd.data, sigma=4)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pcolor(csd["time"], csd["vertical_position"], filtered_csd)

    ax.set_xlabel("time relative to stimulus onset (s)", fontsize=20)
    ax.set_ylabel("vertical position (um)", fontsize=20)

    plt.show()
else:
    filtered_csd_plot = Image.open(Path(resources_dir) /
                          'ecephys_session' /
                          'filtered_csd_plot.png')
    display(filtered_csd_plot)
```

### Suggested exercises

If you would hands-on experience with the `EcephysSession` class, please
consider working through some of these excercises.

- **tuning curves** : Pick a stimulus parameter, such as orientation on drifting
  gratings trials. Plot the mean and standard error of spike counts for each
  unit at each value of this parameter.
- **signal correlations** : Calculate unit-pairwise correlation coefficients on
  the tuning curves for a stimulus parameter of interest (`numpy.corrcoef` might
  be useful).
- **noise correlations** : Build for each unit a vector of spike counts across
  repeats of the same stimulus condition. Compute unit-unit correlation
  coefficients on these vectors.
- **cross-correlations** : Start with two spike trains. Call one of them "fixed"
  and the other "moving". Choose a set of time offsets and for each offset:
    1. apply the offset to the spike times in the moving train
    2. compute the correlation coefficient between the newly offset moving train
    and the fixed train. You should then be able to plot the obtained
    correlation coeffients as a function of the offset.
- **unit clustering** : First, extract a set of unitwise features. You might
  draw these from the mean waveforms, for instance:
    - mean duration between waveform peak and trough (on the unit's peak
      channel)
    - the amplitude of the unit's trough

    or you might draw them from the unit's spike times, such as:
    - median inter-spike-interval

    or from metadata
    - CCF structure

    With your features in hand, attempt an unsupervised classification of the
    units. If this seems daunting, check out the
    [scikit-learn unsupervised learning documention](https://scikit-learn.org/stable/modules/clustering.html#clustering)
    for library code and examples.
- **population decoding** : Using an `EcephysSession` (and filtering to some
  stimuli and units of interest), build two aligned matrices:
    1. A matrix whose rows are stimulus presentations, columns are units, and
       values are spike counts.
    2. A matrix whose rows are stimulus presentations and whose columns are
       stimulus parameters.

    Using these matrices, train a classifier to predict stimulus conditions
    (sets of stimulus parameter values) from presentationwise population spike
    counts. See the
    [scikit-learn supervised learning tutorial](https://scikit-learn.org/stable/tutorial/statistical_inference/supervised_learning.html)
    for a guide to supervised learning in Python.
