# Visual Behavior Neuropixels

The Visual Behavior Neuropixels dataset consists of electrophysiological recordings of neural activity in mice performing a visual change detection task. Each experiment includes data from up to six Neuropixels probes recording simultaneously in cortex, hippocampus, thalamus and midbrain, while mice were exposed to different sensory and behavioral contexts, including familiar and novel stimuli, as well as active and passive stimulus blocks. Data for each experiment is packaged in Neurodata Without Borders (NWB) files that can be accessed via AllenSDK.

## Technique

This dataset includes multi-regional Neuropixels recordings from up to 6 probes at once. The probes target six visual cortical areas including VISp, VISl, VISal, VISrl, VISam, and VISpm. In addition, multiple subcortical areas are also typically measured, including visual thalamic areas LGd and LP as well as units in the hippocampus and midbrain.

Recordings were made in three genotypes: C57BL6J, Sst-IRES-Cre; Ai32, and Vip-IRES-Cre; Ai32. By crossing Sst and Vip lines to the Ai32 ChR2 reporter mouse, we were able to activate putative Sst+ and Vip+ cortical interneurons by stimulating the cortical surface with blue light during an optotagging protocol at the end of each session.

![probeandopto](/images/probe_diagram_with_optagging.webp)

To relate these neurophysiological recordings to mouse behavior, the timing of behavioral responses (licks) and earned rewards were also recorded, as well as mouse running speed, eye position and pupil area.  In addition, videos were taken from front and side views to capture motor activity like grooming, whisking and postural adjustments.

![behaviordata](/images/behavior_data_example.webp)

## Dataset Summary

Every experimental session consisted of four major stimulus epochs as diagrammed below: 1) an active behavior epoch during which the mouse performed the change detection task, 2) a receptive field characterization epoch during which we presented gabor stimuli and full-field flashes, 3) a passive replay epoch during which we replayed the same stimulus frame-for-frame as the mouse encountered during active behavior, but now with the lick spout removed and 4) an optotagging epoch during which we stimulated the surface of the brain with blue light to activate ChR2-expressing cortical interneurons.

<video src="../_static/videos/sample_session_video.mp4"></video>

![vbnexperimentdiagram](/images/vbn_experimental_session_diagram.webp)

To allow analysis of stimulus novelty on neural responses, two different images sets were used in the recording sessions: G and H (diagrammed below). Both image sets comprised 8 natural images. Two images were shared across the two image sets (purple in diagram), enabling within session analysis of novelty effects. Mice took one of the following three trajectories through training and the two days of recording: 

1) Train on G; see G on the first recording day; see H on the second recording day

2) Train on G; see H on the first recording day; see G on the second recording day

3) Train on H; see H on the first recording day; see G on the second recording day

The numbers in the Training and Recording Workflow bubble below give the total recording sessions of each type in the dataset.

![vbnexperimentnumbers](/images/vbn_image_sets_and_training_trajectories_diagram.webp)
