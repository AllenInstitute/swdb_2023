# Visual Behavior 2-photon

The Visual Behavior 2P project used in vivo 2-photon calcium imaging (also called optical physiology, or “ophys”) to measure the activity of genetically identified neurons in the visual cortex of mice performing a go/no-go visual change detection task. This dataset can be used to evaluate the influence of experience, expectation, and task engagement on neural coding and dynamics in excitatory and inhibitory cell populations. Data for each experiment is packaged in Neurodata Without Borders (NWB) files that can be accessed via AllenSDK.

## Technique

We used single- and multi-plane two-photon imaging approaches to record the activity of populations of neurons across multiple cortical depths and visual areas during change detection behavior. Each population of neurons was imaged repeatedly over multiple days under different sensory and behavioral contexts. 

![experimental_design](/images/vbo_experimental_design.png)

Mice initially perform the task under the microscope with the same set of images they observed during training, which have become highly familiar (each image is viewed thousands of times during training). Mice also undergo several sessions with a novel image set that they had not seen prior to the 2-photon imaging portion of the experiment. Passive viewing sessions are interleaved between active behavior sessions. On passive days, mice are given their daily water before the session (and are thus satiated) and view the stimulus in open loop mode, with the lick spout retracted to indicate that rewards are not available. This allows investigation of the impact of motivation and attention on patterns of neural activity.

Neural activity was measured as calcium fluorescence in cells expressing the genetically encoded calcium indicator GCaMP6 in populations of excitatory, Vip inhibitory, and Sst inhibitory neurons using the transgenic mouse lines listed below. Imaging took place between 75-400um below the cortical surface.

![transgenic_lines](/images/vbo_transgenic_lines.png)

Excitatory: Slc17a7-IRES2-Cre;Camk2a-tTA;Ai93(TITL-GCaMP6f) or Ai94(TITL-GCaMP6s)
Vip inhibitory: Vip-IRES-Cre;Ai148(TIT2L-GCaMP6f-ICL-tTA2)
Sst inhibitory: Sst-IRES-Cre;Ai148(TIT2L-GCaMP6f-ICL-tTA2)

In addition to fluorescence timeseries, animal behavior was recorded, including running speed, pupil diameter, lick times, and reward times. These measures allow evaluation of the relationship of neural activity to behavioral states such as arousal, locomotion, and task engagement, as well as choices and errors during task performance.

![data_streams](/images/vbo_data_streams.png)

## Dataset summary

The full dataset includes neural and behavioral measurements from 107 mice during 704 in vivo 2-photon imaging sessions from 326 unique fields of view, resulting in a total of 50,482 cortical neurons recorded. In addition, the full behavioral training history is available for each mouse, for a total of 4,787 behavior sessions.

![dataset_numbers](/images/vbo_final_dataset.png)

The full behavioral training history of all imaged mice is provided as part of the dataset, allowing investigation into task learning, behavioral strategy, and inter-animal variability. There are a total of 4,787 behavior sessions available for analysis.

Different imaging configurations and stimulus sets were used in different groups of mice, resulting in four unique datasets (indicated by their `project_code` in SDK metadata tables and the schematic below). Two single-plane 2-photon datasets were acquired in the primary visual cortex (VISp). In the `VisualBehavior` dataset, mice were trained with image set A and tested with image set B which was novel to the mice. In the `VisualBehaviorTask1` dataset, mice were trained with image set B and tested with image set A as the novel image set. One multi-plane dataset (`VisualBehahviorMultiscope`) was acquired at 4 cortical depths in 2 visual areas (VISp & VISl) using image set A for training and image set B for novelty. 

![data_variants](/images/vbo_dataset_variants.png)

Another multi-plane dataset (`VisualBehaviorMultiscope4areasx2d`) was acquired at 2 cortical depths in 4 visual areas (VISp, VISl, VISal, VISam). In this dataset, two of the images that became highly familiar during training with image set G were interleaved among novel images in image set H to evaluate the effect of novelty context and behavior state on learned stimulus responses.


## Ophys sessions, experiments, and containers

Each 2-photon imaging session consisted of 4 blocks: 
1) a 5 minute period with gray screen to measure spontaneous activity
2) 60 minutes of change detection task performance
3) another 5 minute period with gray screen
4) 10 repeats of a 30 second movie clip that was shown in all 2P imaging sessions

The repeated movie stimulus at the end of each session serves to drive strong nerual activity across the population to aid in cell segmentation and registration across sessions. It can also be used to analyze drift in neural representations over time. 

![session_structure](/images/vbo_session_structure.png)

The data collected in a single continuous recording is defined as an ophys session and receives a unique ophys_session_id. Each imaging plane in a given session is referred to as an ophys experiment and receives a unique ophys_experiment_id. For single-plane imaging, there is only one imaging plane (i.e. one ophys_experiment_id) per session. For multi-plane imaging, there can be up to 8 imaging planes (i.e. 8 ophys_experiment_ids) per session. Due to our strict QC process, not all multi-plane imaging sessions have exactly 8 experiments, as some imaging planes may not meet our data quality criteria.

![data_structure](/images/vbo_data_structure.png)

We aimed to track the activity of single neurons across the session types described above by targeting the same population of neurons over multiple recording sessions, with only one session recorded per day for a given mouse. The collection of imaging sessions for a given population of cells, belonging to a single imaging plane measured across days, is called an ophys container and receives a unique ophys_container_id. An ophys container can include between 3 and 11 separate sessions for that imaging plane. Mice imaged with the multi-plane 2-photon microscope can have multiple containers, one for each imaging plane recorded across multiple sessions. The session types available for a given container can vary, due to our selection criteria to ensure data quality.

Thus, each mouse can have one or more containers, each representing a unique imaging plane (experiment) that has been targeted on multiple recording days (sessions), under different behavioral and sensory conditions (session types).
