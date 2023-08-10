# Session data

The cell type lookup table data set consists of nwb files of 17 experimental sessions. Each session was recorded from a single mouse on a single day.

## Session epochs
Each session consisted of two experimental epochs: (1) an initial, roughly ten minute long period when the mouse is on the running wheel without any sensory stimuli or performing any task, and (2) a period when laser presentation takes place to determine cellular responses to laser. The first epoch is collected in order to get a baseline response for every unit in the absense of any stimuli. Additionally, strong stimulation of neurons expressing opsins may change their firing dynamics, so we want to make sure to get these baseline responses prior to laser stimulation.

## Running speed
Each session is recorded while the mouse is head-fixed on a running wheel. The mouse is able to run at will. A digital encoder on the wheel allows us to determine the mouse's running speed throughout the session.

## Stimulus table
The identity of the trials that take place over the course of the laser stimulation epoch are stored in the stimulus table, which can be accessed with the following code:

The stimulus table contains the following columns:
* start_time: timestamp at which this trial began
* stop_time: timestamp at which this trial ended
* site: the emission site (out of 14) of the NPopto that was on for this trial
* power: the power of the laser stimulus for this trial (in mW)
* param_group: a short descriptor of the stimulus used in this trial (e.g. 'train' for a train of pulses)
* emission_location: for sessions with multiple probes, which probe was emitting the laser for this trial
* duration: duration of each laser pulse (in seconds)
* rise_time: amount of time it took each pulse to get to full power (in seconds)
* num_pulses: number of laser pulses presented during this trial
* wavelength: wavelength of the laser presented during this trial
* type: short descriptor of the location and color of the laser presented (e.g. 'internal_blue')
* inter_pulse_interval: time between each laser pulse in this session (in seconds)
* stimulus_template_name: name of the template used for this stimulus, which can also be 
