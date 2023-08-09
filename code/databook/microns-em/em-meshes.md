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

(em:meshes)=
# Meshes

When trying to understand the fine 3d morphology of a neuron (e.g. features under 1 micron in scale), meshes are a particularly useful representation.
More precisely, a mesh is a collection of vertices and faces that define a 3d surface.
The exact meshes that one sees in Neuroglancer can also be loaded for analysis and visualization in other tools.

## Downloading Meshes

The easiest tool for downloading MICrONs meshes is [Meshparty](https://github.com/sdorkenw/MeshParty), which is a python module that can be installed with `pip install meshparty`.
Documentation for Meshparty can be found [here](https://meshparty.readthedocs.io/en/latest/).

Once installed, the typical way of getting meshes is by using a "MeshMeta" client that is told both the internet location of the meshes (`cv_path`) and a local directory in which to store meshes (`disk_cache_path`).
Once initialized, the MeshMeta client can be used to download meshes for a given segmentation using its root id (`seg_id`).
The following code snippet shows how to download an example mesh using a directory "`meshes`" as the local storage folder. 

```{code-block} python
from meshparty import trimesh_io
from caveclient import CAVEclient
client = CAVEclient('minnie65_public')

mm = trimesh_io.MeshMeta(
  cv_path=client.info.segmentation_source(),
  disk_cache_path="meshes",
)

root_id = 864691135014128278
mesh = mm.mesh(seg_id=root_id)
```

One convenience of using the `MeshMeta` approach is that if you have already downloaded a mesh for with a given root id, it will be loaded from disk rather than re-downloaded.

If you have to download many meshes, it is somewhat faster to use the bulk `download_meshes` function and use multiple threads via the `n_threads` argument. If you download them to the same folder used for the MeshMeta object, they can be loaded through the same interface.

```{code-block} python
root_ids = [864691135014128278, 864691134940133219]
mm = trimesh_io.download_meshes(
    seg_ids=root_ids,
    target_dir='meshes',
    cv_path=client.info.segmentation_source(),
    n_threads=4, # Or whatever value you choose above one but less than the number of cores on your computer
)
```

```{note}
Meshes can be hundresds of megabytes in size, so be careful about downloading too many if the internet is not acting well or your computer doesn't have much disk space!
```

## Healing Mesh Gaps

```{figure} img/mesh-discontinuity.png
---
align: center
---

Example of a continuous neuron whose mesh has a gap.
```

Many meshes are not actually fully continuous due to small gaps in the segmentation.
However, information collected during proofreading allows one to partially repair these gaps by adding in links where the segmentation was merged across a small gap.
If you are just visualizaing a mesh, these gaps are not a problem, but if you want to do analysis on the mesh, you will want to heal these gaps.
Conveniently, there's a function to do this:

```{code-block} python
mesh.add_link_edges(
    seg_id=864691134940133219, # This needs to be the same as the root id used to download the mesh
    client=client.chunkedgraph,
)
```

## Properties

Meshes have a large number of properties, many of which come from being based on the [Trimesh](https://trimsh.org/) library's mesh format, and others being specific to MeshParty.

Several of the most important properties are:
* `mesh.vertices` : An `N x 3` list of vertices and their 3d location in nanometers, where `N` is the number of vertices.
* `mesh.faces` : An `P x 3` list of integers, with each row specifying a triangle of connected vertex indices.
* `mesh.edges` : An `M x 2` list of integers, with each row specifying a pair of connected vertex indices based off of faces.
* `mesh.edges` : An `M x 2` list of integers, with each row specifying a pair of connected vertex indices based off of faces.
* `mesh.link_edges` : An `M_l x 2` list of integers, with each row specifying a pair of "link edges" that were used to heal gaps based on proofreading edits.
* `mesh.graph_edges` : An `(M+M_l) x 2` list of integers, with each row specifying a pair of graph edges, which is the collection of both `mesh.edges` and `mesh.link_edges`.
* `mesh.csgraph` : A [Scipy Compressed Sparse Graph](https://docs.scipy.org/doc/scipy/reference/sparse.csgraph.html) representation of the mesh as an `NxN` graph of vertices connected to one another using graph edges and with edge weights being the distance between vertices. This is particularly useful for computing shortest paths between vertices.

```{Important}
MICrONs meshes are not generally "watertight", a property that would enable a number of properties to be computed natively by Trimesh. Because of this, Trimesh-computed properties relating to solid forms or volumes like `mesh.volume` or `mesh.center_mass` do not have sensible values and other approaches should be taken. Unfortunately, because of the Trimesh implementation of these properties it is up to the user to be aware of this issue.
```

## Visualization

There are a variety of tools for visualizing meshes in python.
MeshParty interfaces with VTK, a powerful but complex data visualization library that does not always work well in python.
The basic pattern for MeshParty's VTK integration is to create one or more "actors" from the data, and then pass those to a renderer that can be displayed in an interactive approach.
The following code snippet shows how to visualize a mesh using this approach.

```{code-block} python
mesh_actor = trimesh_vtk.mesh_actor(
  mesh,
  color=(1,0,0),
  opacity=0.5,
)
trimesh_vtk.render_actors([mesh_actor])
```

Note that by default, neurons will appear upside down because the coordinate system of the dataset has the y-axis value increasing along the "downward" pia to white matter axis.
More documentation on the MeshParty VTK visualization can be [found here](https://meshparty.readthedocs.io/en/latest/source/meshparty.html).

Other tools worth exploring are [PyVista](https://docs.pyvista.org/), [Polyscope](https://polyscope.run/), [Vedo](https://vedo.embl.es/), [MeshLab](https://www.meshlab.net/), and if you have some existing experience, [Blender](https://www.blender.org/) (see Blender integration by our friends behind [Navis](https://navis.readthedocs.io/en/latest/source/blender.html), a fly-focused framework analyzing connectomics data).

## Masking

One of the most common operations on meshes is to mask them to a particular region of interest.
This can be done by "masking" the mesh with a boolean array of length `N` where `N` is the number of vertices in the mesh, with `True` where the vertex should be kept and `False` where it should be omitted.
There are several convenience functions to generate common masks in the [Mesh Filters](https://meshparty.readthedocs.io/en/latest/source/meshparty.html#module-meshparty.mesh_filters) module.

In the following example, we will first mask out all vertices that aren't part of the largest connected component of the mesh (i.e. get rid of floating vertices that might arise due to internal surfaces) and then mask out all vertices that are more than 20,000 nm away from the soma center.

```{code-block} python
from meshparty import mesh_filters

root_id =864691134940133219 
root_point = client.materialize.tables.nucleus_detection_v0(pt_root_id=root_id).query()['pt_position'].values[0] * [4,4,40]  # Convert the nucleus location from voxels to nanometers via the data resolution.

mesh = mm.mesh(seg_id=root_id)
# Heal gaps in the mesh
mesh.add_link_edges(
    seg_id=864691134940133219,
    client=client.chunkedgraph,
)

# Generate and use the largest component mask
comp_mask = mesh_filters.filter_largest_component(mesh)
mask_filt = mesh.apply_mask(comp_mask)

soma_mask = mesh_filters.filter_spatial_distance_from_points(
    mask_filt,
    root_point,
    20_000, # Note that this is in nanometers
)
mesh_soma = mesh.apply_mask(soma_mask)
```

This resulting mesh is just a small cutout around the soma.

```{figure} img/soma_mesh_cutout.png
---
align: center
---
Soma cutout from a full-neuron mesh.
```
