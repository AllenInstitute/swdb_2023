# Neuropixels electrophysiology

:::{figure} https://allensdk.readthedocs.io/en/latest/_static/neuropixels_data_processing.png
:name: np-data-processing-schematic-ref
:align: center
:width: 800

Neuropixels data processing
:::

Neuropixels probes contain 374 or 383 channels that continuously detect voltage
fluctuations in the surrounding neural tissue. Each channel is split into two
separate data streams, or *bands*, on the probes. The *spike band* is digitized
at 30 kHz, and contains information about action potentials fired by neurons
directly adjacent to the probe. The *LFP band* is digitized at 2.5 kHz, and
records the low-frequency (<1000 Hz) fluctuations that result from synchronized
neural activity over a wider area.

To go from the raw spike-band data to NWB files, we perform the following processing steps:

1. Median-subtraction to remove common-mode noise from the continuous traces
2. High-pass filtering (>150 Hz) and whitening across blocks of 32 channels
3. Spike sorting with [Kilosort2](https://github.com/MouseLand/Kilosort), to
   detect spikes and assign them to individual units
4. Computing the mean waveform for each unit
5. Removing units with artifactual waveforms
6. Computing quality metrics for every unit
7. Computing stimulus-specific tuning metrics

For the LFP band, we:

1. Downsample the signals in space and time (every 4th channel and every 2nd sample)
2. High-pass filter at 0.1 Hz to remove the DC offset from each channel
3. Re-reference to channels outside of the brain to remove common-mode noise

The packaged NWB files contain:

* Spike times, spike amplitudes, mean waveforms, and quality metrics for every unit
* Information about the visual stimulus
* Time series of the mouse’s running speed, pupil diameter, and pupil position
* LFP traces for channels in the brain
* Experiment metadata

All code for data processing and packaging is available in the
[ecephys_spike_sorting](https://github.com/alleninstitute/ecephys_spike_sorting)
and the ecephys section of the AllenSDK.
