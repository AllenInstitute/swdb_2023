# Cell Type Look-up Table

The cell type look-up table dataset is a collection of recordings taken from the mouse striatum with the goal of collecting a ground truth data set detailing the responses of different striatal cell types. Data was collected using extracellular electrophysiology. We used transgenic tools to target expression of light-gated ion channels (e.g. CoChR, ChrimsonR, and ChRmine) in specific cell types. During recordings, mice were awake and head-fixed on a running wheel.

## Background

```{code-cell} ipython3
experiment_container_id = 511510736
session_id = boc.get_ophys_experiments(experiment_container_ids=[experiment_container_id], stimuli=['natural_scenes'])[0]['id']
```