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
  name: swdb2023
---

# Annotation Tables

The `minnie65_public` data release includes a number of annotation tables that help label the dataset.
This section describes the content of each of these tables — [see here for instructions for how to query and filter tables](em:query-tables).
Unless otherwise specificied (i.e. via `desired_resolution`), all positions are in units of 4,4,40 nm/voxel resolution.

## Common Fields

Several fields (or column names) are common to many tables.
These fall into two main classes: the spatial point columns that are how we assign annotations to cells via points in the 3d space and book-keeping columns, that are used internally to track the state of the data.

### Spatial Point Columns

Most tables have one or more **Bound Spatial Points**, which is a location in the 3d space that tells the annotation to remain associated with the root id at that location.
Bound spatial points have will have one prefix, usually `pt` (i.e. "point") and three associated columns with different suffixes: `_position`, `_supervoxel_id`, and `_root_id`.

For a given prefix `{pt}`, the three columns are as follows:

* The `{pt}_position` indicates the location of the point in 3d space.
* The `{pt}_supervoxel_id` indicates a unique identifier in the segmentation, and is mostly internal bookkeeping.
* The `{pt}_root_id` indicates the root id of the annotation at that location.

### Book-keeping Columns

Several columns are common to many or all tables, and mostly used as internal book-keeping.
Rather than describe these for every table, they will just be mentioned briefly here:

```{list-table}
:header-rows: 1

* - Column
  - Description
* - `id`
  - A unique ID specific to the annotation within that table.
* - `created`
  - The date that the annotation was created.
* - `valid`
  - Internal bookkeeping column, should always be `t` for data you can download.
* - `target_id` (optional)
  - Some tables reference other tables, particularly the nucleus table. If present, this column will be the same as `id`.
* - `created_ref` / `valid_ref` / `id_ref` (optional)
  - For reference tables, the data shows both the created/valid/id of the reference annotation and the target annotation. The values with the `_ref` suffix are those of the reference table (usually something like proofreading state or cell type) and the values without a suffix ar ethose of the target table (usually a nucleus). 
```

## Synapse Table

Table name: `pni_synapses_v2`

The only synapse table is `pni_synapses_v2`. This is by far the largest table in the dataset with 337 million entries, one for each synapse.
It contains the following columns (in addition to the bookkeeping columns):

```{dropdown} Column Definitions
```{list-table}
:header-rows: 1

* - Column
  - Description
* - `pre_pt_position` / `pre_pt_supervoxel_id` / `pre_pt_root_id`
  - The bound spatial point data for the presynaptic side of the synapse.
* - `post_pt_position` / `post_pt_supervoxel_id` / `post_pt_root_id`
  - The bound spatial point data for the postsynaptic side of the synapse.
* - `size`
  - The size of the synapse in voxels. This correlates well, but not perfectly, with the surface area of synapse.
* - `ctr_pt_position`
  - A position in the center of the detected synaptic junction. Of all points in the synapse table, this is usually the closest point to the surface (and thus mesh) of both neurons. Because it is at the edge of cells, it is not associated with a root id.
```

## Nucleus Table

Table name: `nucleus_ref_neuron_svm`

Nucleus detection has been used to define unique cells in the dataset.
Distinct from the neuronal segmentation, a convolutional neural network was trained to segment nuclei.
Each nucleus detection was given a unique ID, and the centroid of the nucleus was recorded as well as its volume.
While the table of centroids for all nuclei is `nucleus_detection_v0`, this includes neuronal nuclei, non-neuronal nuclei, and some erroneous detections.
The table `nucleus_ref_neuron_svm` shows the results of a classifier that was trained to distinguish neuronal nuclei from non-neuronal nuclei and errors.
For the purposes of analysis, we recommend using the `nucleus_ref_neuron_svm` table to get the most broad collection of neurons in the dataset.

The key columns of `nucleus_ref_neuron_svm` are:

```{dropdown} Column Definitions
```{list-table} 
:header-rows: 1
:name: Nucleus Table
* - Column
  - Description
* - `id`
  - Soma ID for the cell.
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the nucleus.
* - `classification-system`
  - Describes how the classification was done. All values will be `is_neuron` for this table.
* - `cell_type`
  - The output of the classifier. All values will be either `neuron` or `not-neuron` (glia or error) for this table.
```

Note that the `id` column is the same as the nucleus id.

(em:cell-type-tables)=
## Cell Type Tables

There are several tables that contain information about the cell type of neurons in the dataset, with each table representing a different method of doing the classificaiton.
Because each method requires a different kind of information, not all cells are present in all tables.
Each of the cell types tables has the same format and in all cases the `id` column references the nucleus id of the cell in question.

---
### Predictions from soma/nucleus features

Table name: `aibs_soma_nuc_metamodel_preds_v117`

This table contains the results of a hierarchical classifier trained on features of the cell body and nucleus of cells. This was applied to most cells in the dataset that had complete cell bodies (e.g. not cut off by the edge of the data). For more details, see [Elabbady et al. 2022](https://www.biorxiv.org/content/10.1101/2022.07.20.499976v1). In general, this does a good job, but sometimes confuses layer 5 inhibitory neurons as being excitatory: 
The key columns are:

```{dropdown} Column Definitions
```{list-table}
:header-rows: 1
:name: AIBS Soma Nuc Metamodel Table
* - Column
  - Description
* - `id`
  - Soma ID for the cell.
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus.
* - `classification-system`
  - Either `aibs_neuronal` for neurons (Excitatory or inhibitory) or `aibs_non-neuronal` for non-neurons (glia/pericytes).
* - `cell_type`
  - One of several cell types:
    ```{list-table}
    :header-rows: 1
    * - Cell Type
      - Subclass
      - Description
    * - `23P`
      - Excitatory
      - Layer 2/3 cells 
    * - `4P`
      - Excitatory
      - Layer 4 cells
    * - `5P-IT`
      - Excitatory
      - Layer 5 **i**ntra**t**elencephalic cells
    * - `5P-ET`
      - Excitatory
      - Layer 5 **e**xtra**t**elencephalic cells
    * - `5P-NP`
      - Excitatory
      - Layer 5 near-projecting cells
    * - `6P-IT`
      - Excitatory
      - Layer 6 **i**ntra**t**elencephalic cells
    * - `6P-CT`
      - Excitatory
      - Layer 6 **c**ortico**t**halamic cells
    * - `BC`
      - Inhibitory
      - {term}`Basket cell`
    * - `BPC`
      - Inhibitory
      - {term}`Bipolar cell`. In practice, this was used for all cells thought to be {term}`VIP cell`, not only those with a bipolar dendrite.
    * - `MC`
      - Inhibitory
      - Martinotti cells. In practice, this label was used for all inhibitory neurons that appeared to be {term}`Somatostatin cell`, not only those with a {term}`Martinotti cell` morphology.
    * - `NGC`
      - Inhibitory
      - Neurogliaform cells. In practice, this label also is used for all inhibitory neurons in layer 1, many of which may not be neurogliaform cells although they might be in the same molecular family.
    * - `OPC`
      - Non-neuronal
      - Oligodendrocyte precursor cells
    * - `astrocyte`
      - Non-neuronal
      - Astrocytes
    * - `microglia`
      - Non-neuronal
      - Microglia
    * - `pericyte`
      - Non-neuronal
      - Pericytes
    * - `oligo`
      - Non-neuronal
      - Oligodendrocytes
    ```
```

---
### Coarse prediction from spine detection
Table name: `baylor_log_reg_cell_type_coarse_v1`

This table contains the results of a logistic regression classifier trained on properties of neuronal dendrites. This was applied to many cells in the dataset, but required more data than soma and nucleus features alone and thus more cells did not complete the pipeline. It has very good performance on excitatory vs inhibitory neurons because it focuses on dendritic spines, a characteristic property of excitatory neurons. It is a good table to double check E/I classifications if in doubt.

The key columns are:

```{dropdown} Column Definitions
```{list-table}
:header-rows: 1
:name: AIBS Soma Nuc Metamodel Table
* - Column
  - Description
* - `id`
  - Soma ID for the cell.
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus.
* - `classification-system`
  - `baylor_log_reg_cell_type_coarse` for all entries.
* - `cell_type`
  - `excitatory` or `inhibitory`
```

---
### Fine prediction from dendritic features

Table name: `allen_column_mtypes_v1`

This table contains all neurons within a well-proofread 100 micron square column in {term}`VISp` spanning all layers.
Excitatory neurons and inhibitory neurons were distinguished manually, and subclasses were assigned based on a data-driven clustering of the neuronal features.
Inhibitory neurons were classified based on how they distributed they synaptic outputs onto target cells, while exictatory neurons were classified based on a collection of dendritic features.
For more details, see the section on the [Minnie Column](em:minnie-column) or read the preprint [Schneider-Mizell et al. 2023](https://www.biorxiv.org/content/10.1101/2023.01.23.525290v2).
Note that all cell type labels in this column come from a clustering specific to this paper, and while they are intended to align with the broader literature they are not a direct mapping or a well-established convention.
For a more conventional set of labels on the same set of cells, look at the table `allen_v1_column_types_slanted_ref`.
Cell types in that table align with those in `aibs_soma_nuc_metamodel_preds_v117` above.

The key columns are:


```{dropdown} Column Definitions
```{list-table}
:header-rows: 1
:name: AIBS Soma Nuc Metamodel Table
* - Column
  - Description
* - `id`
  - Soma ID for the cell.
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus.
* - `classification-system`
  - `excitatory` or `inhibitory`.
* - `cell_type`
  - One of several cell types.
    ```{list-table}
    :header-rows: 1
    * - Cell Type
      - Subclass
      - Description
    * - `L2a`
      - Excitatory
      - A cluster of layer 2 (upper layer 2/3) excitatory neurons.
    * - `L2b`
      - Excitatory
      - A cluster of layer 2 (upper layer 2/3) excitatory neurons.
    * - `L3a`
      - Excitatory
      - A cluster of excitatory neurons transitioning between upper and lower layer 2/3.
    * - `L3b`
      - Excitatory
      - A cluster of layer 3 (upper layer 2/3) excitatory neurons.
    * - `L3c`
      - Excitatory
      - A cluster of layer 3 (upper layer 2/3) excitatory neurons.
    * - `L4a`
      - Excitatory
      - The largest cluster of layer 4 excitatory neurons.
    * - `L4b`
      - Excitatory
      - Another cluster of layer 4 excitatory neurons.
    * - `L4c`
      - Excitatory
      - A cluster of layer 4 excitatory neurons along the border with layer 5.
    * - `L5a`
      - Excitatory
      - A cluster of layer 5 IT neurons at the top of layer 5.
    * - `L5b`
      - Excitatory
      - A cluster of layer 5 IT neurons throughout layer 5.
    * - `L5ET`
      - Excitatory
      - The cluster of layer 5 ET neurons.
    * - `L5NP`
      - Excitatory
      - The cluster of layer 5 NP neurons.
    * - `L6a`
      - Excitatory
      - A cluster of layer 6 IT neurons at the top of layer 6.
    * - `L6b`
      - Excitatory
      - A cluster of layer 6 IT neurons throughout layer 6. Note that this is different than the label "Layer 6b" which refers to a narrow band at the border between layer 6 and white matter.
    * - `L6c`
      - Excitatory
      - A cluster of tall layer 6 cells (unsure if IT or CT).
    * - `L6CT`
      - Excitatory
      - A cluster of tall layer 6 cells matching manual CT labels.
    * - `L6wm`
      - Excitatory
      - A cluster of layer 6 cells along the border with white matter.
    * - `PTC`
      - Inhibitory
      - Perisomatic targeting cells, a cluster of inhibitory neurons that target the soma and proximal dendrites of excitatory neurons. Approximately corresponds to {term}`basket cells`.
    * - `DTC`
      - Inhibitory
      - Dendrite targeting cells, a cluster of inhibitory neurons that target the distal dendrites of excitatory neurons. Most SST cells would be DTCS.
    * - `STC`
      - Inhibitory
      - Sparsely targeting cells, a cluster of inhibitory neurons that don't concentrate multiple synapses onto the same target neurons. Many neurogliaform cells and layer 1 interneurons fall into this category.  
    * - `ITC`
      - Inhibitory
      - Inhibitory targeting cells, a cluster of inhibitory neurons that preferntially target other inhibitory neurons. Most {term}`VIP cell`s would be ITCs.
    ```
```

---

(em:proofreading-tables)=
## Proofreading Tables

Table name: `proofreading_status_public_release`

The table `proofreading_status_public_release` describes the status of cells selected for manual proofreading.
Because of the inherent difference in the challenge and time required for different kinds of proofreading, we describe the status of axons and dendrites separately.
Further, we distinguish three different categories of proofreading:

* `non`: No proofreading has been comprehensively performed.
* `clean`: Proofreading has comprehensively removed false merges, but not necessarily added missing parts.
* `extended`: Proofreading has comprehensively removed false merges and attempted to add all or most missing parts.

Note that many cells not in this table have been edited in some places, but not comprehensively worked on.
For more information, please see [Proofreading and Data Quality](em:proofreading-data-quality).

The key columns are:

```{dropdown}  Column Definitions
```{list-table} 
:header-rows: 1

* - Column
  - Description
* - `id`
  - ID within the proofreading table (not cell id).
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus being proofread.
* - `valid_id`
  - The root id of the neuron when it the proofreading assessment was made.
* - `status_dendrite`
  - The status of the dendrite proofreading. One of the three categories described above.
* - `status_axon`
  - The status of the axon proofreading. One of the three categories described above.
```


---
(em:functional-coreg)=
## Functional Coregistration Tables

To relate the structural data to functional data, cell bodies must be coregistered between the functional imaging and EM volumes.
The results of this coregistration are stored in two tables with the same columns:

* `coregistration_manual_v3` : The results of manually verified coregistration. This table is well-verified, but contains fewer {term}`ROI`s (N=12,052 root ids, 13,925 ROIs).
* `apl_functional_coreg_forward_v5` : The results of automated functional matching between the EM and 2-p functional data. This table is not manually verified, but contains more {term}`ROI`s (N=36,078 root ids, 68,873 ROIs).

Please see the [Functional Data](em:functional-data) section for more information about using this data.

The column descriptions are:

```{dropdown}  Column Definitions
```{list-table} 
:header-rows: 1

* - Column
  - Description
* - `id`
  - Soma ID for the cell.
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus being proofread.
* - `session`
  - The session index from functional imaging.
* - `scan_idx`
  - The scan index from functional imaging.
* - `unit_id`
  - The ROI index from functional imaging. Only unique within scan and session.
* - `field`
  - The field index from functional imaging.
* - `residual`
  - The residual distance between the functional and the assigned structural points after transformation, in microns.
  Smaller values indicate a closer match.
* - `score`
  - A separation score, measuring the difference between the residual distance to the assigned neuron and the distance to the nearest non-assigned neuron, in microns.
  This can be negative if the non-assigned neuron is closer than the assigned neuron.
  Larger values indicate fewer nearby neurons that could be confused with the assigned neuron.
```



---

## All Tables

```{list-table}
:header-rows: 1
:name: Annotation Tables

* - Table Name
  - Number of Annotations
  - Description
* - `pni_synapses_v2`
  - 337,312,429
  - The locations of synapses and the segment ids of the pre and post-synaptic automated synapse detection.
* - `nucleus_detection_v0`
  - 144,120
  - The locations of nuclei detected via a fully automated method.
* - `nucleus_alternative_points`
  - 8,388
  - A reference annotation table marking alternative segment_id lookup locations for a subset of nuclei in nucleus_detection_v0 that is more accurate than the centroid location listed there.
* - `nucleus_ref_neuron_svm`
  - 144,120
  - A reference annotation indicating the output of a model detecting which nucleus detections are neurons versus which are not.1
* - `coregistration_manual_v4`
  - 13,658
  - A table indicating the association between individual units in the functional imaging data and nuclei in the structural data, derived from human powered matching. Includes residual and separation scores to help assess confidence.
* - `apl_functional_coreg_forward_v5`
  - 68,436
  - A table indicating the association between individual units in the functional imaging data and nuclei in the structural data, derived from the automated procedure. Includes residuals and separation scores to help assess confidence.
* - `proofreading_status_public_release`
  - 1272
  - A table indicating which neurons have been proofread on their axons or dendrites.
* - `proofreading_strategy`
  - 1039
  - A reference table on “proofreading_status_public_release” indicating what axon proofreading strategy was executed on each neuron.
* - `proofreading_edits`
  - 121,271
  - A table containing the number of edits on every segment_id associated with a nucleus in the volume.
* - `aibs_column_nonneuronal_ref`
  - 542
  - Cell type reference annotations from a human expert of non-neuronal cells located amongst the Minnie Column.
* - `allen_v1_column_types_slanted_ref`
  - 1,357
  - Neuron cell type reference annotations from human experts of neuronal cells located amongst the Minnie Column.
* - `allen_column_mtypes_v1`
  - 1,357
  - Neuron cell type reference annotations from data driven unsupervised clustering of neuronal cells 
* - `aibs_soma_nuc_exc_mtype_preds_v117`
  - 58,624
  - Reference annotations indicating the output of a model predicting cell types across the dataset based on the labels from allen_column_mtypes_v1.1
* - `aibs_soma_nuc_metamodel_preds_v117`
  - 86,916
  - Reference annotations indicating the output of a model predicting cell classes based on the labels from allen_v1_column_types_slanted_ref and aibs_column_nonneuronal_ref.
* - `baylor_log_reg_cell_type_coarse_v1`
  - 55,063
  - Reference annotations indicated the output of a logistic regression model predicting whether the nucleus is part of an excitatory or inhibitory cell.50
* - `baylor_gnn_cell_type_fine_model_v2`
  - 49,051
  - Reference annotations indicated the output of a graph neural network model predicting the cell type based on the human labels in allen_v1_column_types_slanted_ref.
