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

# Key Tables

The `minnie65_public` data release includes a number of annotation tables that help label the dataset.
This section describes the content of each of these tables — [see here for instructions for how to query and filter tables](em:query-tables).
Unless otherwise specificied (i.e. via `desired_resolution`), all positions are in units of 4,4,40 nm/voxel resolution.

## Spatial Points

Most tables have one or more **Bound Spatial Points**, which is a location in the 3d space that tells the annotation to remain associated with the root id at that location.
Bound spatial points have will have one prefix, usually `pt` (i.e. "point") and three associated columns with different suffixes: `_position`, `_supervoxel_id`, and `_root_id`.

For a given prefix `{pt}`, the three columns are as follows:

* The `{pt}_position` indicates the location of the point in 3d space.
* The `{pt}_supervoxel_id` indicates a unique identifier in the segmentation, and is mostly internal bookkeeping.
* The `{pt}_root_id` indicates the root id of the annotation at that location.

## Bookkeeping Columns

Several columns are common to many or all tables, and mostly used as internal booking.
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

The only synapse table is `pni_synapses_v2`. This is by far the largets table in the dataset, and is used to get neuronal connectiivty.
It contains the following columns (in addition to the bookkeeping columns):

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

Nucleus detection has been used to define unique cells in the dataset.
Distinct from the neuronal segmentation, a convolutional neural network was trained to segment nuclei.
Each nucleus detection was given a unique ID, and the centroid of the nucleus was recorded as well as its volume.
While the table of centroids for all nuclei is `nucleus_detection_v0`, this includes neuronal nuclei, non-neuronal nuclei, and some erroneous detections.
The table `nucleus_ref_neuron_svm` shows the results of a classifier that was trained to distinguish neuronal nuclei from non-neuronal nuclei and errors.
For the purposes of analysis, we recommend using the `nucleus_ref_neuron_svm` table to get the most broad collection of neurons in the dataset.

The key columns of `nucleus_ref_neuron_svm` are:

```{list-table}
:header-rows: 1
:name: Nucleus Table
* - Column
  - Description
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the nucleus.
* - `classification-system`
  - Describes how the classification was done. All values will be `is_neuron` for this table.
* - `cell_type`
  - The output of the classifier. All values will be either `neuron` or `not-neuron` (glia or error) for this table.
```

Note that the `id` column is the same as the nucleus id.

## Cell Type Tables

There are several tables that contain information about the cell type of neurons in the dataset, with each table representing a different method of doing the classificaiton.
Because each method requires a different kind of information, not all cells are present in all tables.
Each of the cell types tables has the same format and in all cases the `id` column references the nucleus id of the cell in question.

---
`aibs_soma_nuc_metamodel_preds_v117`

This table contains the results of a hierarchical classifier trained on features of the cell body and nucleus of cells. This was applied to most cells in the dataset that had complete cell bodies (e.g. not cut off by the edge of the data). For more details, see [Elabbady et al. 2022](https://www.biorxiv.org/content/10.1101/2022.07.20.499976v1). In general, this does a good job, but sometimes confuses layer 5 inhibitory neurons as being excitatory: 
The key columns are:

```{list-table}
:header-rows: 1
:name: AIBS Soma Nuc Metamodel Table
* - Column
  - Description
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus.
* - `classification-system`
  - Either `aibs_neuronal` for neurons (Excitatory or inhibitory) or `aibs_non-neuronal` for non-neurons (glia/pericytes).
* - `cell_type`
  - One of several cell types. Exictatory neurons are:
    ```{list-table}
    * - Cell Type
      - Description
    * - `23P`
      - Layer 2/3 cells (excitatory)
    * - `4P`
      - Layer 4 cells (excitatory)
    * - `5P-IT`
      - Layer 5 **i**ntra**t**elencephalic cells (excitatory)
    * - `5P-ET`
      - Layer 5 **e**xtra**t**elencephalic cells (excitatory)
    * - `5P-NP`
      - Layer 5 near-projecting cells (excitatory)
    * - `6P-IT`
      - Layer 6 **i**ntra**t**elencephalic cells (excitatory)
    * - `6P-CT`
      - Layer 6 **c**ortico**t**halamic cells (excitatory)
    * - `BC`
      - {term}`Basket cell` (inhibitory)
    * - `BPC`
      - Bipolar (inhibitory). In practice, this was used for all cells thought to be {term}`VIP cell`, not only those with a bipolar dendrite.
    * - `MC`
      - Martinotti cells (inhibitory). In practice, this label was used for all inhibitory neurons that appeared to be {term}`Somatostatin cell`, not only those with a {term}`Martinotti cell` morphology.
    * - `NGC`
      - Neurogliaform cells (inhibitory). In practice, this label also is used for all inhibitory neurons in layer 1, many of which may not be neurogliaform cells although they might be in the same molecular family.
    * - `OPC`
      - Oligodendrocyte precursor cells (non-neuronal)
    * - `astrocyte`
      - Astrocytes (non-neuronal)
    * - `microglia`
      - Microglia (non-neuronal)
    * - `pericyte`
      - Pericytes (non-neuronal)
    * - `oligo`
      - Oligodendrocytes (non-neuronal)
    ```
```

---
`baylor_log_reg_cell_type_coarse_v1`

This table contains the results of a logistic regression classifier trained on properties of neuronal dendrites. This was applied to many cells in the dataset, but required more data than soma and nucleus features alone and thus more cells did not complete the pipeline. It has very good performance on excitatory vs inhibitory neurons because it focuses on dendritic spines, a characteristic property of excitatory neurons. It is a good table to double check E/I classifications if in doubt.

The key columns are:

```{list-table}
:header-rows: 1
:name: AIBS Soma Nuc Metamodel Table
* - Column
  - Description
* - `pt_position` \ `pt_supervoxel_id` \ `pt_root_id`
  - Bound spatial point columns associated with the centroid of the cell nucleus.
* - `classification-system`
  - `baylor_log_reg_cell_type_coarse` for all entries.
* - `cell_type`
  - `excitatory` or `inhibitory`
```

---
`allen_soma_nuc_metamodel_preds_v117


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
  - A reference table on “proofreading_status_public_release” indicating what axon proofreading strategy was executed on each neuron. (see methods)
* - `proofreading_edits`
  - 121,271
  - A csv file indicating the number of edits on every segment_id associated with a nucleus in the volume.
* - `aibs_column_nonneuronal_ref`
  - 542
  - Cell type reference annotations from a human expert of non-neuronal cells located amongst the column defined by.2
* - `allen_v1_column_types_slanted_ref`
  - 1,357
  - Neuron cell type reference annotations from human experts of neuronal cells located amongst the column defined by.2 
* - `allen_column_mtypes_v1`
  - 1,357
  - Neuron cell type reference annotations from data driven unsupervised clustering of neuronal cells 
* - `aibs_soma_nuc_exc_mtype_preds_v117`
  - 58,624
  - Reference annotations indicating the output of a model predicting cell types across the dataset based on the labels from allen_column_mtypes_v1.1
* - `aibs_soma_nuc_metamodel_preds_v117`
  - 86,916
  - Reference annotations indicating the output of a model predicting cell classes based on the labels from allen_v1_column_types_slanted_ref and aibs_column_nonneuronal_ref.1
* - `baylor_log_reg_cell_type_coarse_v1`
  - 55,063
  - Reference annotations indicated the output of a logistic regression model predicting whether the nucleus is part of an excitatory or inhibitory cell.50
* - `baylor_gnn_cell_type_fine_model_v2`
  - 49,051
  - Reference annotations indicated the output of a graph neural network model predicting the cell type based on the human labels in allen_v1_column_types_slanted_ref.50
