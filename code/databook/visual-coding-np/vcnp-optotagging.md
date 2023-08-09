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

# Optotagging Analysis

## Tutorial overview

This Jupyter notebook will demonstrate how to analyze responses to optotagging
stimuli in Neuropixels Brain Observatory datasets. Optotagging makes it possible
to link _in vivo_ spike trains to genetically defined cell classes. By
expressing a light-gated ion channel (in this case, ChR2) in a Cre-dependent
manner, we can activate Cre+ neurons with light pulses delivered to the cortical
surface. Units that fire action potentials in response to these light pulses are
likely to express the gene of interest.

Of course, there are some shortcomings to this approach, most notably that the
presence of light artifacts can create the appearance of false positives, and
that false negatives (cells that are Cre+ but do not respond to light) are
nearly impossible to avoid. We will explain how to deal with these caveats in
order to incorporate the available cell type information into your analyses.

This tutorial will cover the following topics:

* {ref}`content:references:optotag-datasets`
* {ref}`content:references:optotagging-stim`
* {ref}`content:references:opto-alignment`
* {ref}`content:references:cre-units`
* {ref}`content:references:genotype-differences`

This tutorial assumes you've already created a data cache, or are working with
NWB files on AWS. If you haven't reached that step yet, we recommend going
through the {doc}`data access tutorial<vcnp-data-access>` first.

Functions related to analyzing responses to visual stimuli will be covered in
other tutorials. For a full list of available tutorials, see the
[SDK documentation](https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html).



First, let's deal with the necessary imports:

```{code-cell} ipython3
import os

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
%matplotlib inline

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
```

Next, we'll create an `EcephysProjectCache` object that points to a new or existing manifest file.

If you're not sure what a manifest file is or where to put it, please check out
{doc}`data access tutorial<vcnp-data-access>` before going further.

```{code-cell} ipython3
# Example cache directory path, it determines where downloaded data will be stored
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
```

```{code-cell} ipython3
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
```

```{code-cell} ipython3
manifest_path = os.path.join(output_dir, "manifest.json")

cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
```


(content:references:optotag-datasets)=
## Finding datasets of interest



The `sessions` table contains information about all the experiments available in
the `EcephysProjectCache`. The `full_genotype` column contains information about
the genotype of the mouse used in each experiment.

```{code-cell} ipython3
sessions = cache.get_session_table()

sessions.full_genotype.value_counts()
```



About half the mice are wild type (`wt/wt`), while the other half are a cross
between a Cre line and the Ai32 reporter line. The Cre mice express ChR2 in one
of three interneuron subtypes: Parvalbumin-positive neurons (`Pvalb`),
Somatostatin-positive neurons (`Sst`), and Vasoactive Intestinal Polypeptide
neurons (`Vip`). We know that these genes are expressed in largely
non-overlapping populations of inhibitory cells, and that, taken together, they
[cover nearly the entire range of cortical GABAergic neurons](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3556905/#!po=8.92857),
with the caveat that VIP+ cells are a subset of a larger group of
5HT3aR-expressing cells.

To find experiments performed on a specific genotype, we can filter the sessions
table on the `full_genotype` column:

```{code-cell} ipython3
pvalb_sessions = sessions[sessions.full_genotype.str.match('Pvalb')]

pvalb_sessions
```

The table above contains 8 sessions, 5 of which used the `brain_observatory_1.1`
visual stimulus, and 3 of which used the `functional_connectivity` stimulus. Any
experiments with the same stimulus set are identical across genotypes.
Importantly, the optotagging stimulus does not occur until the end of the
experiment, so any changes induced by activating a specific set of interneurons
will not affect the visual responses that we measure.

(content:references:optotagging-stim)=
## Types of optotagging stimuli

Let's load one of the above sessions to see how to extract information about the
optotagging stimuli that were delivered.

```{code-cell} ipython3
session = cache.get_session_data(pvalb_sessions.index.values[-3])
```

The optotagging stimulus table is stored separately from the visual stimulus
table. So instead of calling `session.stimulus_presentations`, we will use
`session.optogenetic_stimulation_epochs` to load a DataFrame that contains the
information about the optotagging stimuli:

```{code-cell} ipython3
session.optogenetic_stimulation_epochs
```

This returns a table with information about each optotagging trial. To find the
unique conditions across all trials, we can use the following Pandas syntax:

```{code-cell} ipython3
columns = ['stimulus_name', 'duration','level']

session.optogenetic_stimulation_epochs.drop_duplicates(columns).sort_values(by=columns).drop(columns=['start_time','stop_time'])
```

The optotagging portion of the experiment includes four categories of blue light
stimuli: 2.5 ms pulses delivered at 10 Hz for one second, a single 5 ms pulse, a
single 10 ms pulse, and a raised cosine pulse lasting 1 second. All of these
stimuli are delivered through a 400 micron-diameter fiber optic cable positioned
to illuminate the surface of visual cortex. Each stimulus is delivered at one of
three power levels, defined by the peak voltage of the control signal delivered
to the light source, not the actual light power at the tip of the fiber.

Unfortunately, light power has not been perfectly matched across experiments. A
little more than halfway through the data collection process, we switched from
delivering light through an LED (maximum power at fiber tip = 4 mW) to a laser
(maximum power at fiber tip = 35 mW), in order to evoke more robust optotagging
responses. To check whether or not a particular experiment used a laser, you can
use the following filter:

```{code-cell} ipython3
sessions.index.values >= 789848216
```



We realize that this makes it more difficult to compare results across
experiments, but we decided it was better to improve the optotagging yield for
later sessions than continue to use light levels that were not reliably driving
spiking responses.

(content:references:opto-alignment)=
## Aligning spikes to light pulses

Aligning spikes to light pulses is a bit more involved than aligning spikes to
visual stimuli. This is because we haven't yet created convenience functions for
performing this alignment automatically, such as
`session.presentationwise_spike_times` or
`sesssion.presentationwise_spike_counts`. We are planning to incorporate such
functions into the AllenSDK in the future, but for now, you'll have to write
your own code for extracting spikes around light pulses (or copy the code
below).

Let's choose a stimulus condition (10 ms pulses) and a set of units (visual
cortex only), then create a DataArray containing binned spikes aligned to the
start of each stimulus.

```{code-cell} ipython3
trials = session.optogenetic_stimulation_epochs[(session.optogenetic_stimulation_epochs.duration > 0.009) & \
                                                (session.optogenetic_stimulation_epochs.duration < 0.02)]

units = session.units[session.units.ecephys_structure_acronym.str.match('VIS')]

time_resolution = 0.0005 # 0.5 ms bins

bin_edges = np.arange(-0.01, 0.025, time_resolution)

def optotagging_spike_counts(bin_edges, trials, units):

    time_resolution = np.mean(np.diff(bin_edges))

    spike_matrix = np.zeros( (len(trials), len(bin_edges), len(units)) )

    for unit_idx, unit_id in enumerate(units.index.values):

        spike_times = session.spike_times[unit_id]

        for trial_idx, trial_start in enumerate(trials.start_time.values):

            in_range = (spike_times > (trial_start + bin_edges[0])) * \
                       (spike_times < (trial_start + bin_edges[-1]))

            binned_times = ((spike_times[in_range] - (trial_start + bin_edges[0])) / time_resolution).astype('int')
            spike_matrix[trial_idx, binned_times, unit_idx] = 1

    return xr.DataArray(
        name='spike_counts',
        data=spike_matrix,
        coords={
            'trial_id': trials.index.values,
            'time_relative_to_stimulus_onset': bin_edges,
            'unit_id': units.index.values
        },
        dims=['trial_id', 'time_relative_to_stimulus_onset', 'unit_id']
    )

da = optotagging_spike_counts(bin_edges, trials, units)
```

We can use this DataArray to plot the average firing rate for each unit as a
function of time:

```{code-cell} ipython3
def plot_optotagging_response(da):

    plt.figure(figsize=(5,10))

    plt.imshow(da.mean(dim='trial_id').T / time_resolution,
               extent=[np.min(bin_edges), np.max(bin_edges),
                       0, len(units)],
               aspect='auto', vmin=0, vmax=200)

    for bound in [0.0005, 0.0095]:
        plt.plot([bound, bound],[0, len(units)], ':', color='white', linewidth=1.0)

    plt.xlabel('Time (s)')
    plt.ylabel('Unit #')

    cb = plt.colorbar(fraction=0.046, pad=0.04)
    cb.set_label('Mean firing rate (Hz)')

plot_optotagging_response(da)
```



In this plot, we can see that a number of units increase their firing rate during the stimulus window, firing a burst of around three spikes. This is typical for Parvalbumin-positive neurons, which fire at high rates under natural conditions.

However, there are also some units that seem to fire at the very beginning and/or very end of the light pulse. These spikes are almost certainly artifactual, as it takes at least 1 ms to generate a true light-evoked action potential. Therefore, we need to disregard these low-latency "spikes" in our analysis.


(content:references:cre-units)=
## Identifying Cre+ units



Now that we know how to align spikes, we can start assessing which units are
reliably driven by the optotagging stimulus and are likely to be Cre+.

There are a variety of ways to do this, but these are the most important things
to keep in mind:
* Spikes that occur precisely at the start or end of a light pulse are likely
  artifactual, and need to be ignored.
* The bright blue light required for optotagging _can_ be seen by the mouse, so
  any spikes that occur more than 40 ms after the stimulus onset may result from
  retinal input, as opposed to direct optogenetic drive.
* The rate of false negatives (Cre+ cells that are not light-driven) will vary
  across areas, across depths, and across sessions. We've tried our best to
  evenly illuminate the entire visual cortex, and to use light powers that can
  drive spikes throughout all cortical layers, but some variation is inevitable.

For these reasons, we've found that the 10 ms pulses are the most useful
stimulus for finding true light-evoked activity. These pulses provide a long
enough artifact-free window to observe light-evoked spikes, but do not last long
enough to be contaminated by visually driven activity.

Using the DataArray we created previously, we can search for units that increase
their firing rate during the 10 ms pulse:

```{code-cell} ipython3
baseline = da.sel(time_relative_to_stimulus_onset=slice(-0.01,-0.002))

baseline_rate = baseline.sum(dim='time_relative_to_stimulus_onset').mean(dim='trial_id') / 0.008

evoked = da.sel(time_relative_to_stimulus_onset=slice(0.001,0.009))

evoked_rate = evoked.sum(dim='time_relative_to_stimulus_onset').mean(dim='trial_id') / 0.008
```

Comparing the baseline and evoked rates, we can see a clear subset of units with
a light-evoked increase in firing rate:

```{code-cell} ipython3
plt.figure(figsize=(5,5))

plt.scatter(baseline_rate, evoked_rate, s=3)

axis_limit = 250
plt.plot([0,axis_limit],[0,axis_limit], ':k')
plt.plot([0,axis_limit],[0,axis_limit*2], ':r')
plt.xlim([0,axis_limit])
plt.ylim([0,axis_limit])

plt.xlabel('Baseline rate (Hz)')
_ = plt.ylabel('Evoked rate (Hz)')
```

We can select a threshold, such as 2x increase in firing rate (red line) to find
the IDs for units that are robustly driven by the light:

```{code-cell} ipython3
cre_pos_units = da.unit_id[(evoked_rate / (baseline_rate + 1)) > 2].values # add 1 to prevent divide-by-zero errors

cre_pos_units
```

Because this is a Parvalbumin-Cre mouse, we expect the majority of light-driven
units to be fast-spiking interneurons. We can check this by plotting the mean
waveforms for the units we've identified.

```{code-cell} ipython3
plt.figure(figsize=(5,5))

for unit_id in cre_pos_units:

    peak_channel = session.units.loc[unit_id].peak_channel_id
    wv = session.mean_waveforms[unit_id].sel(channel_id = peak_channel)

    plt.plot(wv.time * 1000, wv, 'k', alpha=0.3)

plt.xlabel('Time (ms)')
plt.ylabel('Amplitude (microvolts)')
_ =plt.plot([1.0, 1.0],[-160, 100],':c')
```

Indeed, most of these units have stereotypical "fast-spiking" waveforms (with a
peak earlier than 1 ms). The outliers are likely parvalbumin-positive pyramidal
cells.

(content:references:genotype-differences)=
## Differences across genotypes

The example above is a "best-case" scenario. As you look across experiments, you
will find that there is substantial variability in the fraction of light-driven
neurons. Some of this can be accounted for by differences in light power. But
much of the variability can be attributed to genotype: parvalbumin+ cells are
the most abundant type of inhibitory cells in the cortex, with somastatin+ cells
coming next, and VIP+ cells a distant third. There are also likely differences
in our ability to record from different interneuron subtypes. For example,
parvalbumin+ cells generally fire at the highest rates, which makes them easier
to detect in extracellular electrophysiology experiments. The size of the cell's
soma also plays a role in its recordability, and this likely varies across
interneuron sub-classes.

Overall, it is clear that VIP+ cells have proven the most difficult to identify
through optotagging methods. The VIP-Cre mice we've recorded contain _very_ few
light-driven units: the number is on the order of one per probe, and is
sometimes zero across the whole experiment. We're not yet sure whether this is
due to the difficultly of recording VIP+ cells with Neuropixels probes, or the
difficulty of driving them with ChR2. To confounding things even further, VIP+
cells tend to have a _disinhibitory_ effect on the local circuit, so units that
significantly increase their firing during the 1 s raised cosine light stimulus
are not guaranteed to be Cre+.

In any case, it will be helpful to look at some characteristic examples of
light-evoked responses in Sst-Cre and Vip-Cre mice, so you know what to expect.

```{code-cell} ipython3
sst_sessions = sessions[sessions.full_genotype.str.match('Sst')]

session = cache.get_session_data(sst_sessions.index.values[-1])
```

```{code-cell} ipython3
trials = session.optogenetic_stimulation_epochs[(session.optogenetic_stimulation_epochs.duration > 0.009) & \
                                                (session.optogenetic_stimulation_epochs.duration < 0.02)]

units = session.units[session.units.ecephys_structure_acronym.str.match('VIS')]

bin_edges = np.arange(-0.01, 0.025, 0.0005)

da = optotagging_spike_counts(bin_edges, trials, units)
```

```{code-cell} ipython3
plot_optotagging_response(da)
```

In this Sst-Cre mouse, we see a smaller fraction of light-driven units than in
the Pvalb-Cre mouse. The light-driven units tend to spike at a range of
latencies following light onset, rather than displaying the rhythmic firing
pattern of Parvalbumin+ cells. Again, note that the spikes that are precisely
aligned to the light onset or offset are likely artifactual.

Now that we've computed the average responses, we can use the same method as
above to find the units that are activated by the light.

```{code-cell} ipython3
baseline = da.sel(time_relative_to_stimulus_onset=slice(-0.01,-0.002))

baseline_rate = baseline.sum(dim='time_relative_to_stimulus_onset').mean(dim='trial_id') / 0.008

evoked = da.sel(time_relative_to_stimulus_onset=slice(0.001,0.009))

evoked_rate = evoked.sum(dim='time_relative_to_stimulus_onset').mean(dim='trial_id') / 0.008
```

```{code-cell} ipython3
plt.figure(figsize=(5,5))

plt.scatter(baseline_rate, evoked_rate, s=3)

axis_limit = 175
plt.plot([0,axis_limit],[0,axis_limit], ':k')
plt.plot([0,axis_limit],[0,axis_limit*2], ':r')
plt.xlim([0,axis_limit])
plt.ylim([0,axis_limit])

plt.xlabel('Baseline rate (Hz)')
_ = plt.ylabel('Evoked rate (Hz)')
```

There are a smaller fraction of light-driven units in this Sst-Cre mouse, but the effect of optogenetic stimulation is still obvious. Let's look at the waveforms for the units that increase their firing rate at least 2x above baseline:

```{code-cell} ipython3
cre_pos_units = da.unit_id[(evoked_rate / (baseline_rate + 1)) > 2].values

plt.figure(figsize=(5,5))

for unit_id in cre_pos_units:

    peak_channel = session.units.loc[unit_id].peak_channel_id
    wv = session.mean_waveforms[unit_id].sel(channel_id = peak_channel)

    plt.plot(wv.time * 1000, wv, 'k', alpha=0.3)

plt.xlabel('Time (ms)')
plt.ylabel('Amplitude (microvolts)')
_ =plt.plot([1.0, 1.0],[-160, 100],':c')
```

As expected, we see a mix of fast-spiking and regular-spiking waveforms, in
contrast to the primarily fast-spiking waveforms of the Parvalbumin+ units.

Now, let's take a look at light-evoked activity in a VIP-Cre mouse:

```{code-cell} ipython3
vip_sessions = sessions[sessions.full_genotype.str.match('Vip')]

session = cache.get_session_data(vip_sessions.index.values[-1])
```

```{code-cell} ipython3
trials = session.optogenetic_stimulation_epochs[(session.optogenetic_stimulation_epochs.duration > 0.009) & \
                                                (session.optogenetic_stimulation_epochs.duration < 0.02)]

units = session.units[session.units.ecephys_structure_acronym.str.match('VIS')]

bin_edges = np.arange(-0.01, 0.025, 0.0005)

da = optotagging_spike_counts(bin_edges, trials, units)
```

```{code-cell} ipython3
plot_optotagging_response(da)
```

This response looks much different than the examples above. There is only one
unit (out of more than 350 in cortex) that is obviously responding to the 10 ms
light pulse. Even though the yield for VIP-Cre mice is extremely low, these
units will be extremely valuable to analyze. If we can characterize the
stereotypical firing patterns displayed by labeled VIP+ interneurons, we may be
able to identify them in unlabeled recordings.
