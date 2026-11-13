# GOBKINEMATICS

**A Python library for the graphical representation and kinematic classification of geological faults.**

GOBKINEMATICS is a Python library designed to support structural geology analysis through the graphical representation and kinematic classification of geological faults.

It integrates with Matplotlib, allowing users to create and customize geological fault representations using a dedicated plotting projection.

## Features

- Structural fault data representation.
- Kinematic classification and visualization.
- Complete and compact representation modes.
- Customization of STRIKE, FAULT, and AUX graphical elements.
- Optional connectors between STRIKE and FAULT.
- Integration with Matplotlib.
- Input normalization and validation.

## Installation

Once GOBKINEMATICS is published on PyPI, install it using:

```bash
pip install gobkinematics
```

## Requirements

- Python
- NumPy
- Matplotlib

Pandas is optional.

## Quick start

Import GOBKINEMATICS and Matplotlib:

```python
import matplotlib.pyplot as plt
import GOBKINEMATICS
```

Create two plotting axes using the `kinematic` projection:

```python
fig, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(16, 8),
    subplot_kw={"projection": "kinematic"}
)
```

Plot geological faults using the complete and compact representation modes:

```python
ax1.plot_general_faults(
    strike, dip, rake, cine_1, cine_2, "complete"
)

ax2.plot_general_faults(
    strike, dip, rake, cine_1, cine_2, "compact"
)

plt.show()
```

The variables `strike`, `dip`, `rake`, `cine_1`, and `cine_2` represent the structural and kinematic input data.

## Development status

**Version:** 0.1.0  
**Status:** Experimental prototype  
**Language:** Python

GOBKINEMATICS is under active development. This initial experimental release is intended for evaluation by geologists, researchers, and developers working in structural geology.

Future releases may incorporate additional features, data import tools, annotations, and report generation.

## Feedback and contributions

Feedback, suggestions, bug reports, and recommendations are welcome.

Contributions from the structural geology and scientific programming communities are encouraged.

## Repository

[GitHub – Metalic-Ado/GOBKINEMATICS](https://github.com/Metalic-Ado/GOBKINEMATICS)