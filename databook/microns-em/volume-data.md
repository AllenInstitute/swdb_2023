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

# Imagery and Segmentation

We recommend using [ImageryClient](https://github.com/AllenInstitute/ImageryClient) to download imagery and segmentation data.
ImageryClient makes core use of [CloudVolume](https://github.com/seung-lab/cloud-volume/), but adds convenience and better integration with the CAVEclient.

You can install ImageryClient with `pip install pip install imageryclient`.

ImageryClient is designed to download aligned blocks of imagery and segmentation data, as well as has some convenience functions for creating overlays of the two.
A simple example of using ImageryClient to download and visualize a 512x512 pixel cutout of imagery and segmentation centered on a specific location is shown below:

More detailed information can be found in the [documentation](https://github.com/AllenInstitute/ImageryClient).

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
