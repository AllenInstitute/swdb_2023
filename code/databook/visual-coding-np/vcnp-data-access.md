---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: allensdk
  language: python
  name: allensdk
---

# Data access

```{code-cell} ipython3
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
```

```{code-cell} ipython3
# Example cache directory path, it determines where downloaded data will be stored
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
```

The main entry point is the `EcephyProjectCache` class. This class is
responsible for downloading any requested data or metadata as needed and storing
it in well known locations. For this workshop, all of the data has been
preloaded onto the hard drives you have received, and is available on AWS.

We begin by importing the `EcephysProjectCache` class and instantiating it.

`manifest_path` is a path to the manifest file. We will use the manifest file
preloaded onto your Workshop hard drives. Make sure that `drive_path` is set
correctly for your platform. (See the first cell in this notebook.)

```{code-cell} ipython3
#cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
manifest_path = '/data/allen-brain-observatory/visual-coding-neuropixels/ecephys-cache/manifest.json' 

cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
```

## Exploring available sessions of the dataset

:::{admonition} Example: Get information about what's in the Neuropixels dataset

Use the `get_sessions` function from `EcephysProjectCache` to retrieve a
dataframe of all the available sessions. What information does this dataframe
contain?

* How many sessions are there in the dataset?
* What is the average number of units in an experiment? The max number? The minimum?
* What are the different genotypes that were used in these experiments? How many sessions per genotype?
* What are all the brain structures that data has been collected from?
:::

```{code-cell} ipython3
sessions = cache.get_session_table()
```

```{code-cell} ipython3
:tags: [output_scroll]
sessions.head()
```

How many sessions are available?

```{code-cell} ipython3
sessions.shape[0]
```

What's the average number of units in a session? The max? The min?

```{code-cell} ipython3
print(sessions.unit_count.mean())
print(sessions.unit_count.max())
print(sessions.unit_count.min())
```

```{code-cell} ipython3
plt.hist(sessions.unit_count, bins=20);
plt.xlabel("Unit count")
plt.ylabel("# sessions")
```

What are the different genotypes that were used for this dataset? How many
sessions per genotype are available?

```{code-cell} ipython3
sessions.full_genotype.value_counts()
```

What are the different session types? How many sessions per type?

```{code-cell} ipython3
sessions.session_type.value_counts()
```

What are all the structures that data has been collected from?

```{code-cell} ipython3
all_areas = []
for index,row in sessions.iterrows():
    for a in row.ecephys_structure_acronyms:
        if a not in all_areas:
            all_areas.append(a)
```

```{code-cell} ipython3
print(all_areas)
```

To get more information about these structures, visit
[our reference atlas web app](http://atlas.brain-map.org/atlas?atlas=602630314).

How many sessions have data from VISp?

```{code-cell} ipython3
count=0
for index,row in sessions.iterrows():
    if 'VISp' in row.ecephys_structure_acronyms:
        count+=1
print(count)
```

## The session object
The session object contains all the data and metadata for a single experiment
session, including spike times, stimulus information, unit waveforms and derived
metrics, LFP, and the mouse's running speed.

The session object is accessed using `cache.get_session_data(session_id)`

:::{note}
Experiment data is loaded upon initialization of the class. Some data can be
accessed directly as an attribute of the class, others by using 'get' functions.
:::

:::{admonition} Example: Select a session
Let's pick one session to examine in greater detail. Select a
`brain_observatory_1.1` session. Feel free to use other metadata to select one
session and get the session_id (the index).
:::

```{code-cell} ipython3
session_id = sessions[(sessions.unit_count>900)&(sessions.session_type=='brain_observatory_1.1')
                      &(sessions.full_genotype=='wt/wt')].index[0]
print(session_id)
```

Which areas were recorded from in this session?

```{code-cell} ipython3
sessions.ecephys_structure_acronyms[session_id]
```


:::{admonition} Example: Get the data for this session.

Use the `get_session_data` function of the cache to get the session object for
this session. This object contains the data that is stored in the NWB file.
:::


```{code-cell} ipython3
session = cache.get_session_data(session_id)
```

