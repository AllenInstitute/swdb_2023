# Session data

The cell type lookup table data set consists of nwb files of 17 experimental sessions. Each session was recorded from a single mouse on a single day.

## Session epochs
Each session consisted of two experimental epochs: (1) an initial, roughly ten minute long period when the mouse is on the running wheel without any sensory stimuli or performing any task, and (2) a period when laser presentation takes place to determine cellular responses to laser. The first epoch is collected in order to get a baseline response for every unit in the absense of any stimuli. Additionally, strong stimulation of neurons expressing opsins may change their firing dynamics, so we want to make sure to get these baseline responses prior to laser stimulation.

To get the timestamps when these epochs begin and end, use the following code:

## Running speed
Each session is recorded while the mouse is head-fixed on a running wheel. The mouse is able to run at will. A digital encoder on the wheel allows us to determine the mouse's running speed throughout the session.

To get the running speed and timestamps, use the following code:

## Stimulus table
The identity of the trials that take place over the course of the laser stimulation epoch are stored in the stimulus table, which can be accessed with the following code:

The stimulus table contains the following columns:
