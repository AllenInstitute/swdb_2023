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

# Programmatic Access

```{important}
Before using any programmatic access to the data, [you first need to set up your CAVEclient token](em-content:cave-setup).
```

## CAVEclient

Most programmatic access to the CAVE services occurs through CAVEclient, a Python client to access various types of data from the online services.
Full documentation for CAVEclient [is available here](http://caveclient.readthedocs.io).

To initialize a caveclient, we give it a **datastack**, which is a name that defines a particular combination of imagery, segmentation, and annotation database.
For the MICrONs public data, we use the datastack name `minnie65_public`.

```{code-cell}
from caveclient import CAVEclient
datastack_name = 'minnie65_public'
client = CAVEclient(datastack_name)

# Show the description of the datastack
client.info.get_datastack_info()['description']
```

## CAVEclient Basics 

The most frequent use of the CAVEclient is to query the database for annotations like synapses.
All database functions are under the `client.materialize` property.
To see what tables are available, use the `get_tables` function:

```{code-cell}
client.materialize.get_tables()
```

For each table, you can see the metadata describing that table.
For example, let's look at the `nucleus_detection_v0` table:

```{code-cell}
client.materialize.get_table_metadata('nucleus_detection_v0')
```

You get a dictionary of values. Two fields are particularly important: the `description`, which offers a text description of the contents of the table and `voxel_resolution` which defines how the coordinates in the table are defined, in nm/voxel.

## Querying Tables

To get the contents of a table, use the `query_table` function.
This will return the whole contents of a table without any filtering, up to for a maximum limit of 200,000 rows.
The table is returned as a Pandas DataFrame and you can immediately use standard Pandas function on it.

```{code-cell}
cell_type_df = client.materialize.query_table('nucleus_detection_v0')
cell_type_df.head()
```

```{important}
While most tables are small enough to be returned in full, the synapse table has hundreds of millions of rows and is too large to download this way
```

Tables have a collection of columns, some of which specify point in space (columns ending in `_position`), some a root id (ending in `_root_id`), and others that contain other information about the object at that point.
Before describing some of the most important tables in the database, it's useful to know about a few advanced options that apply when querying any table.

* `desired_resolution` : This parameter allows you to convert the columns specifying spatial points to different resolutions.
Many tables are stored at a resolution of 4x4x40 nm/voxel, for example, but you can convert to nanometers by setting `desired_resolution=[1,1,1]`.
* `split_positions` : This parameter allows you to split the columns specifying spatial points into separate columns for each dimension.
The new column names will be the original column name with `_x`, `_y`, and `_z` appended.
* `select_columns` : This parameter allows you to get only a subset of columns from the table.
Once you know exactly what you want, this can save you some cleanup.
* `limit` : This parameter allows you to limit the number of rows returned.
If you are just testing out a query or trying to inspect the kind of data within a table, you can set this to a small number to make sure it works before downloading the whole table.
Note that this will show a warning so that you don't accidentally limit your query when you don't mean to.

For example, using all of these together:
```{code-cell}
cell_type_df = client.materialize.query_table('nucleus_detection_v0', split_positions=True, desired_resolution=[1,1,1], select_columns=['pt_position', 'pt_root_id'], limit=10)
cell_type_df
```

## Key Tables 

## Querying Synapses

While synapses are stored as any other table in the database, in this case `synapses_pni_2`, this table is much larger than any other table at more than 337 million rows, and it works best when queried in a different way.
The `synapse_query` function allows you to query the synapse table in a more convenient way than most other tables.
In particular, the `pre_ids` and `post_ids` let you specify which root id (or collection of root ids) you want to query, with pre_ids indicating the collection of presynaptic neurons and post_ids the collection of postsynaptic neurons.
Using both `pre_ids` and `post_ids` in one call is effectively a logical AND, returning only those synapses from neurons in the list of `pre_ids` that target neurons in the list of `post_ids`.
Let's look at one particular example.
  
  ```{code-cell}
my_root_id = 864691135808473885
syn_df = client.materialize.synapse_query(pre_ids=my_root_id)
print(f"Total number of output synapses for {my_root_id}: {len(syn_df)}")
syn_df.head()
```

The columns from a synapse query are:
```{list-table}
:header-rows: 1

* - Column
  - Description
* - `id`
  - A unique ID specific to the synapse annotation
* - `pre_pt_position`
  - The position of the presynaptic side of the synapse. 
* - `pre_pt_supervoxel_id`
  - A bookkeeping column for the presynaptic side
* - `pre_pt_root_id`
  - The root id of the presynaptic neuron
* - `post_pt_position`
  - The position of the postsynaptic side of the synapse
* - `post_pt_supervoxel_id`
  - A bookkeeping column for the postsynaptic side
* - `post_pt_root_id`
  - The root id of the postsynaptic neuron
* - `size`
  - The size of the synapse in voxels. This correlates well, but not perfectly, with the surface area of synapse.
* - `ctr_pt_position`
  - The position of the center of the synapse. This is usually closest to the surface (and thus mesh) of both neurons.
```
Unless otherwise specificied (i.e. via `desired_resolution`), positions are in units of 4,4,40 nm/voxel resolution.

Note that synapse queries always return the list of every synapse between the neurons in the query, even if there are multiple synapses between the same pair of neurons.

A common pattern to generate a list of connections between unique pairs of neurons is to group by the root ids of the presynaptic and postsynaptic neurons and then count the number of synapses between them.
For example, to get the number of synapses from this neuron onto every other neuron, ordered

```{code-cell}
syn_df.groupby(
  ['pre_pt_root_id', 'post_pt_root_id']
).count()[['id']].sort_values(
  by='id',
  ascending=False,
)
# Note that the [['id']] part here is just a way to quickly extract one column.
# This could be any of the remaining column names.

```