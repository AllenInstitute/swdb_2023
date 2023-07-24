#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# # Dataset
# 
# We will start exploring the parameters of the dataset to learn what data is available. 
# 
# First we need to access the dataset. We will use the AllenSDK and the BrainObservatoryCache to do so. First we need to set this up - the key step is to provide a <b>manifest file</b>. The SDK uses this file to know what data is available and organize the files it downloads. If you instantiate the BrainObservatoryCache without proviing a manifest file, it will create one in your working directory.

# In[2]:


from allensdk.core.brain_observatory_cache import BrainObservatoryCache
boc = BrainObservatoryCache()


# We can use the BrainObservatoryCache to explore the parameters of the dataset. 
# 
# ## Targeted structures
# What brain regions were recorded across the dataset? To determine this we use a function called `get_all_targeted_structures()` to create a list of the regions.

# In[3]:


boc.get_all_targeted_structures()


# We see that data was collected in six different visual areas. VISp is the primary visual cortex, also known as V1. The others are higher visual areas that surround VISp. See [visual cortical areas](../background/anatomy.md) to learn more about these areas and how we map them.
# 
# ## Cre lines and reporters
# We used Cre lines to drive the expression of GCaMP6 in specific populations of neurons. We can find a list of all the cre lines used in this dataset with a similar function

# In[4]:


boc.get_all_cre_lines()


# Cre is a driver that drives the expression of a reporter. We used four different reporter lines in this dataset.

# In[5]:


boc.get_all_reporter_lines()


# ```{note}
# Reporter lines: All the experiments in this dataset use GCaMP6. The large majority use GCaMP6f and only a few use GCaMP6s. However, you see four different reporters listed here. Why is this? Ai93 is the GCaMP6f reporter we used with the excitatory Cre lines. However, this reporter does not work well for inhibitory Cre lines. We used Ai148, another GCaMP6f reporter, with Vip-IRES-Cre and Sst-IRES-Cre. However, this didn't work with the Pvalb-IRES-Cre. We use Ai162, a GCaMP6s reporter with Pvalb. Additionally, to have a GCaMP6f vs GCaMP6s comparison, we collected a small number of experiments using Ai94 with the Slc17a7-IRES2-Cre. This is a GCaMP6s reporter that complements Ai93. Slc17a7-IRES2-Cre is the only Cre line that was recorded using multiple reporter types. 
# ```
# 
# See [Transgenic tools](../background/transgenic-tools.md) to learn more about these Cre lines and reporters.
# 
# (imaging_depths)=
# ## Imaging depths
# Each experiment was collected at a single imaging depth.

# In[6]:


boc.get_all_imaging_depths()


# These values are in um below the surface of the cortex. This is a long list and some of the values don't differ by very much. How meaningful is it? We roughly consider depths less than 250 to be layer 2/3, 250-350 to be layer 4, 350-500 to be layer 5, and over 500 to be layer 6. Keep in mind, much of the imaging here was done with layer specific Cre lines, so for most purposes the best way to get layer specificity is to select appropriate Cre lines.
# 
# ## Visual stimuli
# What were the visual stimuli that we showed to the mice?

# In[7]:


boc.get_all_stimuli()


# These are described more extensively in [Visual stimuli](vc2p-stimuli.md).
# 
# (experiment_containers_sessions)=
# ## Experiment containers & sessions
# The <b>experiment container</b> describes a set of 3 imaging <b>sessions</b> performed for the same field of view (ie. same targeted structure and imaging depth in the same mouse that targets the same set of neurons). Each experiment container has a unique ID number.
# 
# We will identify all the experiment containers for a given stucture and Cre line:

# In[8]:


visual_area = 'VISp'
cre_line ='Cux2-CreERT2'

exps = boc.get_experiment_containers(targeted_structures=[visual_area], cre_lines=[cre_line])


# ```{note}
# `get_experiment_containers` returns all experiment containers that meet the conditions we have specified. The parameters that we could pass this function include targeted_structures, imaging_depths, cre_lines, reporter_lines, stimuli, session_types, and cell_specimen_ids. If we don't pass any parameters, it returns all experiment containers.
# ```
# 
# We can make a dataframe of the list of experiment containers to see what information we get about them:

# In[9]:


pd.DataFrame(exps)


# id
# : The <b>experiment container id</b>
# 
# imaging_depth
# : The [imaging depth](imaging_depths) that data was acquired at, in um from the surface of cortex.
# 
# targeted_structure
# : The brain structure that was imaged in this session.
# 
# cre_line	
# : The {term}`Cre line` that the mouse has.
# 
# reporter_line
# : The {term}`Reporter line` that the mouse has.
# 
# donor_name
# : The id of the mouse that was imaged.
# 
# specimen_name
# : The full name of the mouse including its genotype and donor name.
# 
# tags
# : A list of tags
# 
# failed
# : Boolean indicating whether the experiment container failed QC. By default, only container that pass QC are returned. Users must specify to include failed experiment containers if looking for these. 
# 
# You see there are 16 experiments for this Cre line in VISp. They all have different <b>experiment container ids</b> (called "id" here) and they mostly have different <b>donor names</b> which identify the mouse that was imaged. This Cre line was imaged at two different imaging depths, sampling both layer 2/3 and layer 4. But they all have the same Cre line, targeted structure and reporter line.
# 
# 
# ## Exercise: How many experiment containers were collected in each cortical visual area for each Cre line?

# In[10]:


cre_lines = boc.get_all_cre_lines()
areas = boc.get_all_targeted_structures()
df = pd.DataFrame(columns=areas, index=cre_lines)
for cre in cre_lines:
  for area in areas:
    exps = boc.get_experiment_containers(targeted_structures=[area], cre_lines=[cre])
    df[area].loc[cre] = len(exps)
df


# You see that not all Cre lines were imaged in all areas. 
# 
# ## Session types
# The responses to this full set of visual stimuli were recorded across three imaging sessions. We returned to the same targeted structure and same imaging depth in the same mouse to recorded the same group of neurons across three different days. 
# 
# Let's look at all of the sessions in a single experiment container.

# In[11]:


experiment_container_id = 511510736
sessions = boc.get_ophys_experiments(experiment_container_ids=[experiment_container_id])
pd.DataFrame(sessions)


# id
# : The <b>session id</b> for the session. 
# 
# imaging_depth
# : The [imaging depth](imaging_depths) that data was acquired at, in um from the surface of cortex.
# 
# targeted_structure
# : The brain structure that was imaged in this session.
# 
# cre_line	
# : The {term}`Cre line` that the mouse has.
# 
# reporter_line
# : The {term}`Reporter line` that the mouse has.
# 
# acquisition_age_days
# : The age of the mouse when this session was recorded, in days.
# 
# experiment_container_id
# : The id of the experiment container that this session belongs to.
# 
# session_type	
# : The name of the session, this describes the set of stimuli that are presented during the experiment.
# 
# donor_name
# : The id of the mouse that was imaged.
# 
# specimen_name
# : The full name of the mouse including its genotype and donor name.
# 
# fail_eye_tracking
# : Boolean marking which sessions had successful eye tracking. This might be obsolete.
# 
# When looking at all of the sessions in a single experiment container, as we have done above, you will notice that the experiment container id, cre line, reporter line, donor name, specimen name, imaging depth, targeted structure are all the same while the id, acquisition age, and session type must be different.
# 
# As you see, each experiment container has three different session types. For the data published in June 2016 and October 2016, the last session is <b>three_session_C</b<> while the data published after this were collected using <b>three_session_C2</b>. The key difference between these sessions is a change in the [locally sparse noise](locally_sparse_noise) stimulus.
# 
# ![containers](/images/VC2p-sessions.png)
# 
# ## Cell specimen ids
# During data processing, we matched identified {term}`ROI`s (REFERENCE) across each of the sessions within experiment containers. Approximately one third of the neurons in the dataset were matched across all three sessions, one third were matched in two of the three session, and one third were only found in one session. Neurons have unique ids, called <b>cell_specimen_ids</b>, that are shared across the sessions they are found in.
# 
# ```{admonition} Why do we not match ROIs across all three session for all neurons? 
# :class: tip
# There are a few factors that could explain why we don't always match ROIs across all sessions that include biological, experimental, and analytical reasons. Biologically, a neuron must be active within a session to be identifiable during segmentation. For various reasons, a neuron might not be active during some sessions while it is active during others. Experimentally, there are challenges to returning to the precise same field of view. Being at a slightly different depth, or having just a bit of tilt in the imaging plane, might result in some neurons that were in view during one session not being in view during another. Analytically, the method for identifying {term}`ROI`s as well as for matching ROIs from multiple sessions can make mistakes.
# ```
# 
# We explore how to look at neurons across session in [Cross session data](vc2p-cross-session-data.md).
