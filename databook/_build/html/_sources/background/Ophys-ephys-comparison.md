# Ophys ephys comparison

Extracellular electrophysiology (ephys) and two-photon calcium imaging (ophys) are widely used methods for measuring physiological activity with single-cell resolution across large populations of cortical neurons. While each of these two modalities has distinct advantages and disadvantages, neither provides complete, unbiased information about the underlying neural population. As a result, we need to undersand how scientific conclusions may be skewed by the recording modalities to best interpret data. 

There are some key differences that are readily apparent between ephys and ophys. For starters, spatial sampling is inherently different between the two modalities. Two-photon calcium imaging typically yields data in a single plane tangential to the cortical surface, and is limited to depths of <1 mm due to a combination of light scattering and absorption in tissue. Even with multiplane imaging, these planes are almost always orthogonal to the surface of these cortex. Extracellular electrophysiology, on the other hand, utilizes microelectrodes embedded in the tissue, and thus dense recordings are easiest to perform along a straight line, normal to the cortical surface, in order to minimize per-channel tissue displacement. Linear probes provide simultaneous access to neurons in both cortex and subcortical structures, but make it difficult to sample many neurons from the same cortical layer.

![2pNP](/images/2p-NP.png)

The temporal resolutions of these two methodologies also differ in critical ways. Imaging is limited by the dwell time required to capture enough photons to distinguish physiological changes in fluorescence from noise, and the kinetics of calcium- dependent indicators additionally constrain the ability to temporally localize neural activity. While kilohertz-scale imaging has been achieved, most studies are based on data sampled at frame rates between 1 and 30 Hz. In contrast, extracellular electrophysiology requires sampling rates of 20 kHz or higher in order to capture the action potential waveform shape that is essential for accurate spike sorting. High sampling rates allow extracellular electrophysiology to pin-point neural activity in time with sub-millisecond resolution. 

[box: can we see single spikes w/ ca imaging? Point to 2p method page for spatial/temporal trade off]

We took advantage of our two complementary datasets to compare evoked responses in visual cortex recorded in awake mice under highly standardized conditions using either imaging of genetically expressed GCaMP6f [LINK TO VC2P] or electrophysiology using Neuropixels probes [LINK TO VCNP]. We found that there were some marked differences in the responses across the population in the two modalities, and were able to account for a large part of these differences.

The differences that we observed could largely be account for by a few keys things:

## Ephys selection bias
Extracellular electrophysiology has a selection bias for neurons with larger spikes and higher firing rates. Not just in the recording itself, but particularly during the spike sorting process. There need to be enough spikes present to be able to identify and cluster them into a unit. So neurons that are very sparsely active will not be reliably detected using ephys. But these neurons are more likely to be detected in calcium imaging where a neuron only needs to fire a few times in a recording session for it to be successfully identified. 

One way this is apparent is that we see more active and responsive neurons using ephys than we do with ophys. In ophys data we see many more neurons that don't seem to respond to the stimuli or behavior that we use in experiments, raising fundamental questions about what are they doing? Another way is that there tend to be more units isolated in layer 5, where the neurons have large spikes, than in other layers. But the neurons in layer 5 are larger and thus sparser - compare the numbers of neurons in an imaging plane in layer 2/3 with that of a plane in layer 5 in either the <b>Visual Coding 2p</b> or <b>Visual Behavior 2p</b> datasets. There is a higher density of neurons in layer 2/3 than in layer 5.

## Calcium indicators sparsify spiking activity
Calcium indicators exhibit a non-linear response to the firing rate of neurons, such that single spikes are often washed out while 'bursty' spike sequences with short inter-spike intervals are non-linearly boosted. As a result
