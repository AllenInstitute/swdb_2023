# Ophys ephys comparison

Extracellular electrophysiology (ephys) and two-photon calcium imaging (ophys) are widely used methods for measuring physiological activity with single-cell resolution across large populations of cortical neurons. While each of these two modalities has distinct advantages and disadvantages, neither provides complete, unbiased information about the underlying neural population. As a result, we need to undersand how scientific conclusions may be skewed by the recording modalities to best interpret data. 

We took advantage of our two complementary datasets to compare evoked responses in visual cortex recorded in awake mice under highly standardized conditions using either imaging of genetically expressed GCaMP6f [LINK TO VC2P] or electrophysiology using Neuropixels probes [LINK TO VCNP].

There are some key differences that are readily apparent between ephys and ophys. For starters, spatial sampling is inherently different between the two modalities. Two-photon calcium imaging typically yields data in a single plane tangential to the cortical surface, and is limited to depths of <1 mm due to a combination of light scattering and absorption in tissue. Even with multiplane imaging, these planes are almost always orthogonal to the surface of these cortex. Extra-
cellular electrophysiology, on the other hand, utilizes microelectrodes embedded in the tissue, and thus dense recordings are easiest to perform along a straight line, normal to the cortical surface, in order to minimize per-channel tissue displacement. Linear probes provide simultaneous access to neurons in both cortex and subcortical structures, but make it difficult to sample many neurons from the same cortical layer.

![2pNP](/images/2p-NP.png)

The temporal resolutions of these two methodologies also differ in critical ways. Imaging is limited by the dwell time required to capture enough photons to distinguish physiological changes in fluorescence from noise, and the kinetics of calcium- dependent indicators additionally constrain the ability to temporally localize neural activity. While kilohertz-scale imaging has been achieved, most studies are based on data sampled at frame rates between 1 and 30 Hz. In contrast, extracellular electrophysiology requires sampling rates of 20 kHz or higher, in order to capture the action potential waveform shape that is essential for accurate spike sorting. High sampling rates allow extracellular electrophysiology to pin-point neural activity in time with sub-millisecond resolution.

