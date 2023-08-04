---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Visual Behavior Neuropixels Session

Once you've selected a session of interest, the corresponding nwb file can be conveniently accessed through the AllenSDK. <code>VisualBehaviorNeuropixelsProjectCache</code> class. 

Below, we will walk through what's contained in each of these session nwb files. For more examples demonstrating how to analyze these data, please refer to the tutorials [here](https://allensdk.readthedocs.io/en/latest/visual_behavior_neuropixels.html)

We begin by importing the <code>VisualBehaviorNeuropixelsProjectCache</code>  class.

```{code-cell} ipython3
import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

from allensdk.brain_observatory.behavior.behavior_project_cache.\
    behavior_neuropixels_project_cache \
    import VisualBehaviorNeuropixelsProjectCache
```

Now we can specify our cache directory and set up the cache.

```{code-cell} ipython3
# this path should point to the location of the dataset on your platform
cache_dir = '/data/'

cache = VisualBehaviorNeuropixelsProjectCache.from_local_cache(
            cache_dir=cache_dir, use_static_cache=True)
```

We can use the <code>VisualBehaviorNeuropixelsProjectCache</code> to grab the data for one example session:

```{code-cell} ipython3
session_id = 1053941483
session = cache.get_ecephys_session(
            ecephys_session_id=session_id)
```

We can list the attributes and methods associated with this session object as follows:

```{code-cell} ipython3
session.list_data_attributes_and_methods()
```


Now let's see how theses are defined. First we'll group them into a few classes:
 <b>metadata</b>: attributes that contain useful info about each session
 <b>data</b>:     attributes and methods for accessing primary data for this session, including spike data, lfp, licks, running and eye tracking
 <b>tables</b>:   attributes and methods for accessing the tables storing stimulus info, behavior trial info


## Metadata

The following attributes contain metadata about each session. Most of the necessary metadata can be found in the `session.metadata` attribute, including the rig on which this experiment was run, the genotype, age and sex of the mouse and the name of the behavioral script:

```{code-cell} ipython3
session.metadata
```

The following attributes also contain useful info:

`behavior_session_id`:  Unique ID for the behavior session associated with this experiment. 
`task_parameters`:      Dictionary of parameters for this behavioral session as follows:

auto_reward_volume
: Volume of autorewards delivered at beginning of session in ml.

blank_duration_sec
: Seconds of gray screen at beginning and end of behavior session

n_stimulus_frames
: Number of stimulus frames rendered during this experiment

omitted_flash_fraction
: Probability that eligible flashes were omitted

response_window_sec
: The period following an image change, in seconds, during which a mouse response influences trial outcome. The first value represents response window start. The second value represents response window end. The values represent time before display lag is accounted for and applied.

reward_volume
: volume of individual water reward in ml.

session_type
: visual stimulus type displayed during behavior session

stimulus
: stimulus class shown for each image flash

stimulus_distribution
: Probablity distribution used for drawing change times. Either ‘exponential’ or ‘geometric’

stimulus_duration_sec
: duration in seconds of each stimulus image presentation (or 'flash')

task
: type of visual stimulus task; 'change detection' for this dataset

## Ephys Data

The primary ephys data can be accessed through the following attributes and methods. To see examples for how to align neural activity to task and stimulus events, check out the tutorials [here](https://allensdk.readthedocs.io/en/latest/visual_behavior_neuropixels.html).

Let's start by choosing an example unit and extracting its spike times and mean waveform. We can use the `get_units` method to identify a unit of interest. To filter units by their brain structure, it is useful to first merge the units table with the channels table:

```{code-cell} ipython3
units = session.get_units() #get units table
channels = session.get_channels() #get channels table
units_channels = units.merge(channels, left_on='peak_channel_id', right_index=True) #merge the two tables
```

Now we can pull out a few of the units recorded in VISp:

```{code-cell} ipython3
units_channels[units_channels['structure_acronym']=='VISp'].head()
```

Let's take the first unit as our example: 1061854534. Three dictionaries will allow us to access data for this unit:

`spike_times`: dictionary storing spike times for each unit
`spike_amplitudes`: dictionary storing the spike amplitudes for each units in volts
`mean_waveforms`: dictionary storing the mean waveform for each unit as a (channel: 384, sample_number: 82) array

```{code-cell} ipython3
unit_spiketimes = session.spike_times[1061854534]
unit_spike_amplitudes = session.spike_amplitudes[1061854534]
unit_waveform = session.mean_waveforms[1061854534]
```

LFP data can be accessed through the following methods. Keep in mind that LFP data is stored in separate NWB files. Calling these methods will download additional data. For more info about how to access and analyze the LFP data, check out [this tutorial](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/visual_behavior_neuropixels_LFP_analysis.html).

The LFP data is stored as an [xarray.DataArray](http://xarray.pydata.org/en/stable/) object, with coordinates of time and channel. The xarray library simplifies the process of working with N-dimensional data arrays, by keeping track of the meaning of each axis. If this is your first time encountering xarrays, we strongly recommend reading through the documentation before going further. Getting used to xarrays can be frustrating, especially when they don't behave like numpy arrays. But they are designed to prevent common mistakes when analyzing multidimensional arrays, so they are well worth learning more about. Plus, the syntax is modeled on that of the pandas library, so if you're familiar with that you already have a head start.

The LFP for each probe insertion is stored in a separate NWB file. To see what probes were inserted for this experiment, we can look at the `session.probes` table:

```{code-cell} ipython3
session.probes
```

Now we can grab the LFP data for one of these probes (let's take 1054059291). The following line of code will download a lfp NWB file if it's not already part of your cache:

```{code-cell} ipython3
probe_lfp = session.get_lfp(1054059291)
```

Since this LFP has been spatially downsampled, a high resolution CSD has been pre-computed and stored as an xarray.DataArray. You can access this CSD as follows:

```{code-cell} ipython3
probe_csd = session.get_current_source_density(1054059291)
```

## Behavior Data

Each session NWB also contains running, licking and eye tracking data. These data are all stored as pandas dataframes in the session object. For more details about how to align behavioral data to task events, check out [this tutorial](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/aligning_behavioral_data_to_task_events_with_the_stimulus_and_trials_tables.html) 

`session.eye_tracking`: A dataframe containing ellipse fit parameters for the eye, pupil and corneal reflection (cr). Fits are derived from tracking points from a DeepLabCut model applied to video (collected at 60hz) frames of a subject’s right eye.

frame (index)
: *int* frame of eye tracking video. 

timestamps
: *float* experiment timestamp for frame in seconds

likely_blink
: *bool* True if frame has outlier ellipse fits, which is often caused by blinking / squinting of the eye.

eye_area
: *float* area of eye ellipse in pixels squared

eye_area_raw
: *float* pupil area with no outliers/likely blinks removed.

eye_center_x
: *float* center of eye ellipse on x axis in pixels

eye_center_y
: *float* center of eye ellipse on y axis in pixels

eye_height
: *float* eye height (minor axis of the eye ellipse) in pixels

eye_width
: *float* eye width (major axis of the eye ellipse) in pixels

eye_phi
: *float* eye rotation angle in radians

pupil_area
: *float* area of pupil ellipse in pixels squared

pupil_area_raw
: *float* pupil area with no outliers/likely blinks removed.

pupil_center_x
: *float* center of pupil ellipse on x axis in pixels

pupil_center_y
: *float* center of pupil ellipse on y axis in pixels

pupil_height
: *float* pupil height (minor axis of the pupil ellipse) in pixels

pupil_width
: *float* pupil width (major axis of the pupil ellipse) in pixels

pupil_phi
: *float* pupil rotation angle in radians

cr_area
: *float* area of corneal reflection ellipse in pixels squared

cr_area_raw
: *float* corneal reflection area with no outliers/likely blinks removed.

cr_center_x
: *float* center of corneal reflection on x axis in pixels

cr_center_y
: *float* center of corneal reflection on y axis in pixels

cr_height
: *float* corneal reflection height (minor axis of the CR ellipse) in pixels

cr_width
: *float* corneal reflection width (major axis of the CR ellipse) in pixels

cr_phi
: *float* corneal reflection rotation angle in radians


`session.licks`: A dataframe containing lick timestamps and frames, sampled at 60Hz.

timestamps
: *float* time of a lick, in seconds

frame
: *int* frame of lick


`session.running_speed`: Running speed and timestamps sampled at 60hz. A 10Hz low pass filter has been applied to the data. To get the running speed without the filter, use `raw_running_speed`.

speed
: *float* speed in cm/sec

timestamps
: *float* time in seconds


`rewards`: A dataframe containing timestamps of delivered rewards in absolute sync time. Timestamps are sampled at 60 Hz.

timestamps
: *float* time in seconds

volume
: *float* volume of individual water reward in ml.

auto_rewarded
: *bool* True if free reward was delivered for that trial. Occurs during the first 5 trials of a session.


## Behavior Trials Table
Now let's explore the behavior trials table. This table contains lots of useful information about every trial in the change detection task. For more info about how to use this table to align behavioral/neural events, you might find [this tutorial](https://github.com/AllenInstitute/swdb_2022/blob/main/DynamicBrain/solutions/Visual_Behavior_Neuropixels_SWDB_2022_Tutorial_Solutions.ipynb) useful.

```{code-cell} ipython3
trials = session.trials
trials.head()
```

Here, every row is one behavioral trial. The following columns contain all the information you need to interpret each trial:

start_time
: *float* Experiment time when this trial began in seconds.

end_time
: *float* Experiment time when this trial ended.

initial_image_name
: *float* Indicates which image was shown before the change (or sham change) for this trial

change_image_name
: *string* Indicates which image was scheduled to be the change image for this trial. Note that if the trial is aborted, a new trial will begin before this change occurs.

stimulus_change
: *bool* Indicates whether an image change occurred for this trial. 

change_time_no_display_delay
: *float* Experiment time when the task-control computer commanded an image change. This change time is used to determine the response window during which a lick will trigger a reward. Note that due to display lag, this is not the time when the change image actually appears on the screen. To get this time, you need the stimulus_presentations table (more about this below).

go
: *bool* Indicates whether this trial was a 'go' trial. To qualify as a go trial, an image change must occur and the trial cannot be autorewarded.

catch
: *bool* Indicates whether this trial was a 'catch' trial. To qualify as a catch trial, a 'sham' change must occur during which the image identity does not change. These sham changes are drawn to match the timing distribution of real changes and can be used to calculate the false alarm rate.

lick_times
: *float array* A list indicating when the behavioral control software recognized a lick. Note that this is not identical to the lick times from the licks dataframe, which record when the licks were registered by the lick sensor. The licks dataframe should generally be used for analysis of the licking behavior rather than these times.

response_time
: *float* Indicates the time when the first lick was registered by the task control software for trials that were not aborted (go or catch). NaN for aborted trials. For a more accurate measure of response time, the licks dataframe should be used.

reward_time
: *float* Indicates when the reward command was triggered for hit trials. NaN for other trial types. 

reward_volume
: *float* Indicates the volume of water dispensed as reward for this trial. 

hit
: *bool* Indicates whether this trial was a 'hit' trial. To qualify as a hit, the trial must be a go trial during which the stimulus changed and the mouse licked within the reward window (150-750 ms after the change time).

false_alarm
: *bool* Indicates whether this trial was a 'false alarm' trial. To qualify as a false alarm, the trial must be a catch trial during which a sham change occurred and the mouse licked during the reward window.

miss
: *bool* To qualify as a miss trial, the trial must be a go trial during which the stimulus changed but the mouse did not lick within the response window.

correct_reject
: *bool* To qualify as a correct reject trial, the trial must be a catch trial during which a sham change occurred and the mouse withheld licking.

aborted
: *bool* A trial is aborted when the mouse licks before the scheduled change or sham change.

auto_rewarded
: *bool* During autorewarded trials, the reward is automatically triggered after the change regardless of whether the mouse licked within the response window. These always come at the beginning of the session to help engage the mouse in behavior.

change_frame
: *int* Indicates the stimulus frame index when the change (on go trials) or sham change (on catch trials) occurred. This column can be used to link the trials table with the stimulus presentations table, as shown below.

trial_length
: *float* Duration of the trial in seconds.


## Stimulus Presentations Table

This shows us the structure of this experiment (and every experiment in this dataset). There are 5 stimuli as follows:

**block 0**: Change detection task. Natural images are flashed repeatedly and the mouse is rewarded for licking when the identity of the image changes. You can find more info about this task [here](http://portal.brain-map.org/explore/circuits/visual-behavior-neuropixels?edit&language=en). Also see [here](https://www.frontiersin.org/articles/10.3389/fnbeh.2020.00104/full) for info about our general training strategy.

**block 1**: Brief gray screen

**block 2**: Receptive field mapping. Gabor stimuli used for receptive field mapping. For more details on this stimulus consult [this notebook](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_receptive_fields.html).

**block 3**: Longer gray screen

**block 4**: Full-field flashes, shown at 80% contrast. Flashes can be black (color = -1) or white (color = 1).

**block 5**: Passive replay. Frame-for-frame replay of the stimulus shown during the change detection task (block 0), but now with the lick spout retracted so the animal can no longer engage in the task.


Here's a quick explanation for each of the columns in this table:

<b>General</b>

`active`: Boolean indicating when the change detection task (with the lick spout available to the mouse) was run. This should only be TRUE for block 0.

`stimulus_block`: Index of stimulus as described in cells above.

`stimulus_name`: Indicates the stimulus category for this stimulus presentation. 

`contrast`: Stimulus contrast as defined [here](https://www.psychopy.org/api/visual/gratingstim.html#psychopy.visual.GratingStim.contrast)

`duration`: Duration of stimulus in seconds

`start_time`: Experiment time when stimulus started. This value is corrected for display lag and therefore indicates when the stimulus actually appeared on the screen.

`end_time`: Experiment time when stimulus ended, also corrected for display lag.

`start_frame`: Stimulus frame index when this stimulus started. This can be used to sync this table to the behavior trials table, for which behavioral data is collected every frame.

`end_frame`: Stimulus frame index when this stimulus ended.

<b>Change</b> detection task and Passive replay (blocks 0 and 5)

`flashes_since_change`: Indicates how many flashes of the same image have occurred since the last stimulus change.

`image_name`: Indicates which natural image was flashed for this stimulus presentation. To see how to visualize this image, check out [this tutorial](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/visual_behavior_neuropixels_data_access.html).

`is_change`: Indicates whether the image identity changed for this stimulus presentation. When both this value and 'active' are TRUE, the mouse was rewarded for licking within the response window.

`omitted`: Indicates whether the image presentation was omitted for this flash. Most image flashes had a 5% probability of being omitted (producing a gray screen). Flashes immediately preceding a change or immediately following an omission could not be omitted.

`rewarded`: Indicates whether a reward was given after this image presentation. During the passive replay block (5), this value indicates that a reward was issued for the corresponding image presentation during the active behavior block (0). No rewards were given during passive replay.

<b>Receptive field mapping gabor stimulus (block 2)</b>

`orientation`: Orientation of gabor. 

`position_x`: Position of the gabor along azimuth. The units are in degrees relative to the center of the screen (negative values are nasal).

`position_y`: Position of the gabor along elevation. Negative values are lower elevation.

`spatial_frequency`: Spatial frequency of gabor in cycles per degree.

`temporal_frequency`: Temporal frequency of gabor in Hz.

<b>Full field flashes (block 4)</b>

`color`: Color of the full-field flash stimuli. "1" is white and "-1" is black.



## Optotagging Table

id <b>index</b>
: *int* Trial index

condition
: *string* Description of laser waveform used for this trial

duration
: *float* Duration of laser stimulation for this trial

level
: *float* Laser command voltage for this trial (higher values indicate higher power laser stimulation)

start_time
: *float* Start time of laser stimulation for this trial

stimulus_name
: *string* Name of laser waveform used for this trial

stop_time
: *float* Time when laser stimulation stops for this trial





stimulus_templates
stimulus_timestamps





