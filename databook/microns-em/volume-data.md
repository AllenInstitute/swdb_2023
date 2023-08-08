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
  name: swdb2023-em
---

```{important}
Before using any programmatic access to the data, [you first need to set up your CAVEclient token](em-content:cave-setup).
```

# Imagery and Segmentation

We recommend using [ImageryClient](https://github.com/AllenInstitute/ImageryClient) to download imagery and segmentation data.
ImageryClient makes core use of [CloudVolume](https://github.com/seung-lab/cloud-volume/), but adds convenience and better integration with the CAVEclient.

You can install ImageryClient with `pip install pip install imageryclient`.

ImageryClient is designed to download aligned blocks of imagery and segmentation data, as well as has some convenience functions for creating overlays of the two.
Imagery is downloaded as blocks of 8-bit values (0-255) that indicate grayscale intensity, while segmentation is downloaded as blocks of 64-bit integers that describe the segmentation ID of each voxel.
Alternatively, segmentation can be kept as a dictionary of boolean masks, where each key is a root ID and each value is a boolean mask of the same shape as the imagery.

Detailed information on the options can be found in the [documentation](https://github.com/AllenInstitute/ImageryClient).
A typical example would be to use ImageryClien to download and visualize a 512x512 pixel cutout of imagery and segmentation centered on a specific location based on the coordinates in Neuroglancer:


```{code-cell}
import imageryclient as ic
from caveclient import CAVEclient

client = CAVEclient('minnie65_public')

img_client = ic.ImageryClient(client=client)

ctr = [240640, 207872, 21360]

image, segs = img_client.image_and_segmentation_cutout(ctr,
                                                       split_segmentations=True,
                                                       bbox_size=(512, 512),
                                                       scale_to_bounds=True,
)

ic.composite_overlay(segs, imagery=image, palette='husl').convert("RGB")
# Note: the final `.convert('RGB')` is needed to build this documetnation, but is not required to run locally.
```
