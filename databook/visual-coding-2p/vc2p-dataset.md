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
```{code-cell} ipython3
import pandas as pd
```

# Dataset

We will start exploring the parameters of the dataset to learn what data is available. 

First we need to access the dataset. We will use the AllenSDK and the BrainObservatoryCache to do so. First we need to set this up - the key step is to provide a <b>manifest file</b>. The SDK uses this file to know what data is available and organize the files it downloads. If you instantiate the BrainObservatoryCache without proviing a manifest file, it will create one in your working directory.

```{code-cell} ipython3
from allensdk.core.brain_observatory_cache import BrainObservatoryCache
boc = BrainObservatoryCache()
```

We can use the BrainObservatoryCache to explore the parameters of the dataset. 

## Targeted structures
What brain regions were recorded across the dataset? To determine this we use a function called <b>get_all_targeted_structures</b> to create a list of the regions.

```{code-cell} ipython3
boc.get_all_targeted_structures()
```

We see that data was collected in six different visual areas. VISp is the primary visual cortex, also known as V1. The others are higher visual areas that surround VISp. See [visual cortical areas](../background/anatomy.md) to learn more about these areas and how we map them.

## Cre lines and reporters
We used Cre lines to drive the expression of GCaMP6 in specific populations of neurons. We can find a list of all the cre lines used in this dataset with a similar function

```{code-cell} ipython3
boc.get_all_cre_lines()
```

Cre is a driver that drives the expression of a reporter. We used four different reporter lines in this dataset. 

```{code-cell} ipython3
boc.get_all_reporter_lines()
```

```{note}
Reporter lines: All the experiments in this dataset use GCaMP6. The large majority use GCaMP6f and only a few use GCaMP6s. However, you see four different reporters listed here. Why is this? Ai93 is the GCaMP6f reporter we used with the excitatory Cre lines. However, this reporter does not work well for inhibitory Cre lines. We used Ai148, another GCaMP6f reporter, with Vip-IRES-Cre and Sst-IRES-Cre. However, this didn't work with the Pvalb-IRES-Cre. We use Ai162, a GCaMP6s reporter with Pvalb. Additionally, to have a GCaMP6f vs GCaMP6s comparison, we collected a small number of experiments using Ai94 with the Slc17a7-IRES2-Cre. This is a GCaMP6s reporter that complements Ai93. Slc17a7-IRES2-Cre is the only Cre line that was recorded using multiple reporter types. 
```

See [Transgenic tools](../background/transgenic-tools.md) to learn more about these Cre lines and reporters.

## Imaging depths
Each experiment was collected at a single imaging depth. 

```{code-cell} ipython3
boc.get_all_imaging_depths()
```

These values are in um below the surface of the cortex. This is a long list and some of the values don't differ by very much. How meaningful is it? We roughly consider depths less than 250 to be layer 2/3, 250-350 to be layer 4, 350-500 to be layer 5, and over 500 to be layer 6. Keep in mind, much of the imaging here was done with layer specific Cre lines, so for most purposes the best way to get layer specificity is to select appropriate Cre lines.

## Visual stimuli
What were the visual stimuli that we showed to the mice?

```{code-cell} ipython3
boc.get_all_stimuli()
```

These are described more extensively in [Visual stimuli](vc2p-stimuli.md).

## Experiment containers & sessions

The <b>experiment container</b> describes a set of 3 imaging <b>sessions</b> performed for the same field of view (ie. same targeted structure and imaging depth in the same mouse that targets the same set of neurons). Each experiment container has a unique ID number.

We will identify all the experiment containers for a given stucture and Cre line:

```{code-cell} ipython3
visual_area = 'VISp'
cre_line ='Cux2-CreERT2'

exps = boc.get_experiment_containers(targeted_structures=[visual_area], cre_lines=[cre_line])
```

```{note}
<b>get_experiment_containers</b> returns all experiment containers that meet the conditions we have specified. The parameters that we could pass this function include targeted_structures, imaging_depths, cre_lines, and reporter_lines. If we don't pass any parameters, it returns all experiment containers.
```

ids=None,
    experiment_container_ids=None,
    targeted_structures=None,
    imaging_depths=None,
    cre_lines=None,
    reporter_lines=None,
    transgenic_lines=None,
    stimuli=None,
    session_types=None,
    cell_specimen_ids=None,

We can make a dataframe of the list of experiment containers to see what information we get about them:

```{code-cell} ipython3
pd.DataFrame(exps)
```

You see there are 16 experiments for this Cre line in VISp. They all have different <b>experiment container ids</b> (called "id" here) and they mostly have different <b>donor names</b> which identify the mouse that was imaged. This Cre line was imaged at two different imaging depths, sampling both layer 2/3 and layer 4. But they all have the same Cre line, targeted structure and reporter line.


### Exercise: How many experiment containers were collected in VISp for each Cre line?

```{code-cell} ipython3
cre_lines = boc.get_all_cre_lines()
areas = boc.get_all_targeted_structures()
df = pd.DataFrame(columns=areas, index=cre_lines)
for cre in cre_lines:
  for area in areas:
    exps = boc.get_experiment_containers(targeted_structures=[area], cre_lines=[cre])
    df[area].loc[cre] = len(exps)
df
```
You see that not all Cre lines were imaged in all areas. 

## Session types
The responses to this full set of visual stimuli were recorded across three imaging sessions. We returned to the same targeted structure and same imaging depth in the same mouse to recorded the same group of neurons across three different days. 

```{code-cell} ipython3
boc.get_all_session_types()
```

get one container, list the sessions
diagram of three session options from website



We will explore which stimuli are part of which session in [Visual stimuli](vc2p-stimuli.md). 

During data processing, we matched identified {term}`ROI`s (REFERENCE) across each of the sessions within experiment containers. Approximately one third of the neurons in the dataset were matched across all three sessions, one third were matched in two of the three session, and one third were only found in one session. Neurons have unique ids, called <b>cell_specimen_ids</b>, that are shared across the sessions they are found in.

```{admonition} Why do we not match ROIs across all three session for all neurons? 
:class: tip
There are a few factors that could explain why we don't always match ROIs across all sessions that include biological, experimental, and analytical reasons. Biologically, a neuron must be active within a session to be identifiable during segmentation. For various reasons, a neuron might not be active during some sessions while it is active during others. Experimentally, there are challenges to returning to the precise same field of view. Being at a slightly different depth, or having just a bit of tilt in the imaging plane, might result in some neurons that were in view during one session not being in view during another. Analytically, the method for identifying {term}`ROI`s as well as for matching ROIs from multiple sessions can make mistakes.
```

We explore how to look at neurons across session in [Cross session data](vc2p-cross-session-data.md). 
