# Visual Coding 2-photon

The Visual Coding 2-photon dataset is a survey of in vivo physiological activity in the awake mouse cortex. Neural activity was recorded using {term}`Two-photon calcium imaging`. We used transgenic tools to target the expression of a fluorescent calcium indicator, {term}`GCaMP`6, to a specific population of neurons. We collected data across six different visual cortical areas, including {term}`V1` and five {term}`HVA`s, using 14 {term}`Transgenic line`s, and across the cortical layers. 

During imaging, mice were awake, head-fixed under the microscope, and positioned on a running disk that enabled them to run at will. The mice passively viewed an assortment of visual stimuli [visual stimuli](vc2p-stimuli.md) presented on a monitor. Cameras recorded the eye position of the eye pointed at the monitor. Thus, in addition to the neural activity, we also have measured the mouse's running activity, and the pupil position, and pupil area of the mouse's eye. (Keep in mind that the pupil area is largely controlled by the amount of light, which is kept relatively constant during these experiments. Thus the dynamic range of the pupil area is likely less than in non-visual experiments.)

## Background
There is a long history of studying the activity of neurons in the visual system. Some of the earliest work stems from [classic experiments](https://www.youtube.com/watch?v=8VdFf3egwfg) of David Hubel and Torsten Wiesel who had developed the tungsten electrode. Inserting the electrode in the V1 of an anasethized cat, they were able to determine what visual stimulus drove the activity of the neuron they were recording, and in this way they mapped the {term}`receptive field` of the neuron. 
(Add citation to paper)

Over the last sixty years, extensive work has been done using this approach, recording from single or small groups of neurons in V1 as well as other regions of the visual system, characterizing the spatial and temporal features that best drive neurons. Despite decades of this research, there were several outstanding questions:

First, stemming from that initial work of Hubel and Wiesel, the field converged on a standard model for the neurons in V1 in which each neuron's activity is modeled by a spatiotemporal filter followed by a static nonlinearity. Yet, the reality is that such models do not predict many neurons well, particular in response to more naturalistic stimuli.
(cite What other 85% doing, etc)

Second, as neurons in different parts of the visual circuit were found to respond to different features, there were open question as to what the computations were that transformed the simple responses of the neurons in the early visual system into the more complex features.

The <b>Allen Brain Observatory Visual Coding</b> datasets were collected in large part to address these questions. These are survey datasets, recording the physiological activity of neurons in the visual system of the mouse in different parts of the visual circuit in response to a variety of visual stimuli (both "artificial" and "naturalistic"). 

Need survey
“what would be most helpful is to accumulate a database of single-unit or multi-unit data (stimuli and neural responses) that would allow modelers to test their best theory under ecological conditions"

## Visual physiology in mice
While much of the historical, and ongoing, work studying visual physiology was performed in cats and primates, mouse has emerged as a model organism for visual physiology in the past two decades. 
[more here, with references!]

## Technique
For the <b>Visual Coding 2-photon</b> dataset we used [Two-photon calcium imaging](../background/Two-photon-calcium-imaging.md) to record the activity of populations of neurons. We used [transgenic tools](../background/transgenic-tools.md) that use {term}`Cre line`s to drive the expression of {term}`GCaMP`6 in a specific population of neurons. These could be excitatory or inhibitory neurons, they could be broadly expressed or confined to neurons within specific layers or even subtypes within a layer. In this dataset, we performed single plane imaging such that within an experiment we collected data from a population of neurons within a single visual area at a single imaging depth. 

## Experiment
Awake mice were head-fixed under a 2-photon microscope, on a running disc. Their running was self driven, and we see great variability in the amount of running between mice. A population of neurons was targeted to image using the transgenic tools as described. The neurons express {term}`GCaMP`6 such that whenever the neurons are active, the neurons light up. The mice are presented with a variety of [visual stimuli](/vc2p-stimuli.md) and the fluorescence of the neurons is recorded using the 2-photon microscope. In addition to the neural activity, the running speed of the mouse is recorded, along with the position and area of the pupil. The far right panel below shows the eye position of this mouse superimposed on the stimulus that is being shown.

<video controls src="/images/VicCoginExpt.mp4"></video>

## Questions to explore
There are many ways to explore these datasets, so these are not exhaustive by any means.
- Compare single cell visual responses across different types of cells (defined by Cre lines) and different areas.
- Look a population coding. Each imaging session includes a population of neurons. This ranges from roughly a dozen neurons for inhibitory {term}`Interneuron`s to up to 400 neurons for denser excitatory neurons. Can you decode the stimulus from population activity? What is the structure of correlations between neurons in different populations? 
- Compare responses to different types of stimuli. How well can you predict responses to naturalistic stimuli from the responses to artificial stimuli, or vice-versa? Do the correlation structures differ based on the stimulus that is used?
- Explore neural activity (single cell or population) in relation to behavioral variables such as running speed or pupil area/position. Do these differ across areas/Cre lines? 
- Explore behavioral variables (running speed/duration or pupil area/position) by themselves. Do different transgenic lines exhibit different behaviors?



