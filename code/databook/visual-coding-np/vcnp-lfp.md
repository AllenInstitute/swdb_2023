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

# Local Field Potential (LFP)

The final aspect of a Neuropixels probe recording we will investigate is the local field potential (LFP). An LFP signal is a direct recordings of extracellular voltage from which individual spike contributions have been removed by low-pass filtering. The remaining signal reflects the population activity of a large number of cells in the vicinity of the probe, primarily through the electrical field effects of synaptic currents (along with other trans-membrane currents).


LFP can be especially informative for understanding rhythmic activity or oscillations in neural circuits, which can be identified by some simple time-series analysis of the LFP signals.

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
