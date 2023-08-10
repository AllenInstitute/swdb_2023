---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Quick start guide

## Tutorial overview

A short introduction to the Visual Coding Neuropixels data and SDK. For more
information, see the {doc}`full example notebook<./vcnp-session>`.

This tutorial will demonstrate how to make the following:

* {ref}`content:references:psth`
* {ref}`content:references:decoding-images`

```{code-cell}
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from allensdk.brain_observatory.ecephys.ecephys_project_cache import EcephysProjectCache
```

The `EcephysProjectCache` is the main entry point to the Visual Coding Neuropixels dataset. It allows you to download data for individual recording sessions and view cross-session summary information.

```{code-cell}
# Example cache directory path, it determines where downloaded data will be stored
output_dir = '/run/media/galen.lynch/Data/SWDB_2023/visual_coding_neuropixels'
manifest_path = os.path.join(output_dir, "manifest.json")
cache = EcephysProjectCache.from_warehouse(manifest=manifest_path)
print(cache.get_all_session_types())
```

This dataset contains sessions in which two sets of stimuli were presented. The `"brain_observatory_1.1"` sessions are (almost exactly) the same as Visual Coding 2P sessions.

```{code-cell}
sessions = cache.get_session_table()
brain_observatory_type_sessions = sessions[sessions["session_type"] == "brain_observatory_1.1"]
brain_observatory_type_sessions.tail()
```

(content:references:psth)=
## Peristimulus time histograms



We are going to pick a session arbitrarily and download its spike data.

```{code-cell}
session_id = 791319847
session = cache.get_session_data(session_id)
```

We can get a high-level summary of this session by acessing its `metadata` attribute:

```{code-cell}
session.metadata
```

We can also take a look at how many units were recorded in each brain structure:

```{code-cell}
session.structurewise_unit_counts
```

Now that we've gotten spike data, we can create peristimulus time histograms.

```{code-cell}
presentations = session.get_stimulus_table("flashes")
units = session.units[session.units["ecephys_structure_acronym"] == 'VISp']

time_step = 0.01
time_bins = np.arange(-0.1, 0.5 + time_step, time_step)

histograms = session.presentationwise_spike_counts(
    stimulus_presentation_ids=presentations.index.values,
    bin_edges=time_bins,
    unit_ids=units.index.values
)

histograms.coords
```

```{code-cell}
mean_histograms = histograms.mean(dim="stimulus_presentation_id")

fig, ax = plt.subplots(figsize=(8, 8))
ax.pcolormesh(
    mean_histograms["time_relative_to_stimulus_onset"],
    np.arange(mean_histograms["unit_id"].size),
    mean_histograms.T,
    vmin=0,
    vmax=1
)

ax.set_ylabel("unit", fontsize=24)
ax.set_xlabel("time relative to stimulus onset (s)", fontsize=24)
ax.set_title("peristimulus time histograms for VISp units on flash presentations", fontsize=24)

plt.show()
```

(content:references:decoding-images)=
## Decoding visual stimuli

First, we need to extract spikes. We will do using `EcephysSession.presentationwise_spike_times`, which returns spikes annotated by the unit that emitted them and the stimulus presentation during which they were emitted.

```{code-cell}
scene_presentations = session.get_stimulus_table("natural_scenes")
visp_units = session.units[session.units["ecephys_structure_acronym"] == "VISp"]

spikes = session.presentationwise_spike_times(
    stimulus_presentation_ids=scene_presentations.index.values,
    unit_ids=visp_units.index.values[:]
)

spikes
```

Next, we will convert these into a num_presentations X num_units matrix, which will serve as our input data.

```{code-cell}
spikes["count"] = np.zeros(spikes.shape[0])
spikes = spikes.groupby(["stimulus_presentation_id", "unit_id"]).count()

design = pd.pivot_table(
    spikes,
    values="count",
    index="stimulus_presentation_id",
    columns="unit_id",
    fill_value=0.0,
    aggfunc=np.sum
)

design
```

... with targets being the numeric identifiers of the images presented.

```{code-cell}
targets = scene_presentations.loc[design.index.values, "frame"]
targets
```

```{code-cell}
from sklearn import svm
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
```

```{code-cell}
design_arr = design.values.astype(float)
targets_arr = targets.values.astype(int)

labels = np.unique(targets_arr)
```

```{code-cell}
accuracies = []
confusions = []

for train_indices, test_indices in KFold(n_splits=5).split(design_arr):

    clf = svm.SVC(gamma="scale", kernel="rbf")
    clf.fit(design_arr[train_indices], targets_arr[train_indices])

    test_targets = targets_arr[test_indices]
    test_predictions = clf.predict(design_arr[test_indices])

    accuracy = 1 - (np.count_nonzero(test_predictions - test_targets) / test_predictions.size)
    print(accuracy)

    accuracies.append(accuracy)
    confusions.append(confusion_matrix(y_true=test_targets, y_pred=test_predictions, labels=labels))
```

```{code-cell}
print(f"mean accuracy: {np.mean(accuracy)}")
print(f"chance: {1/labels.size}")
```

### imagewise performance

```{code-cell}
mean_confusion = np.mean(confusions, axis=0)

fig, ax = plt.subplots(figsize=(8, 8))

img = ax.imshow(mean_confusion)
fig.colorbar(img)

ax.set_ylabel("actual")
ax.set_xlabel("predicted")

plt.show()
```

```{code-cell}
best = labels[np.argmax(np.diag(mean_confusion))]
worst = labels[np.argmin(np.diag(mean_confusion))]

fig, ax = plt.subplots(1, 2, figsize=(16, 8))

best_image = cache.get_natural_scene_template(best)
ax[0].imshow(best_image, cmap=plt.cm.gray)
ax[0].set_title("most decodable", fontsize=24)

worst_image = cache.get_natural_scene_template(worst)
ax[1].imshow(worst_image, cmap=plt.cm.gray)
ax[1].set_title("least decodable", fontsize=24)


plt.show()
```
