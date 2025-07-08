# napari-debcr

<!--
[![License MIT](https://img.shields.io/pypi/l/napari-debcr.svg?color=green)](https://github.com/DeBCR/napari-debcr/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-debcr.svg?color=green)](https://pypi.org/project/napari-debcr)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-debcr.svg?color=green)](https://python.org)
[![tests](https://github.com/DeBCR/napari-debcr/workflows/tests/badge.svg)](https://github.com/DeBCR/napari-debcr/actions)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-debcr)](https://napari-hub.org/plugins/napari-debcr)
-->

**DeBCR** is a Python-based framework for light microscopy data enhancement, including denoising and deconvolution.

[`napari-debcr`](https://github.com/DeBCR/napari-debcr/) is add-on plugin, created to provide a graphical interface for [DeBCR](https://github.com/DeBCR/DeBCR) in [Napari viewer](https://github.com/napari/napari).

This plugin was initialized with [copier](https://copier.readthedocs.io/en/stable/) using the [napari-plugin-template](https://github.com/napari/napari-plugin-template).

### License
This is an open-source project and is licensed under [MIT license](https://github.com/DeBCR/napari-debcr/blob/main/LICENSE).

### Contact
For any questions or bur-reports related to:
- the [`napari-debcr`](https://github.com/DeBCR/napari-debcr/) plugin - use the [napari-debcr GitHub Issue Tracker](https://github.com/DeBCR/napari-debcr/issues);
- the core [`debcr`](https://github.com/DeBCR/DeBCR) package - use the [DeBCR GitHub Issue Tracker](https://github.com/DeBCR/DeBCR/issues).

## Installation

As for the core package `debcr`, there are two hardware-based installation options for `napari-debcr`:
- `napari-debcr[tf-gpu]` - for a GPU-based trainig and prediction (**recommended**);
- `napari-debcr[tf-cpu]` - for a CPU-only execution (note: training on CPUs might be quite slow!).

### GPU prerequisites

For a GPU version you need:
- a GPU device with at least 12Gb of VRAM;
- a compatible CUDA Toolkit (recommemded: [CUDA-11.7](https://developer.nvidia.com/cuda-11-7-0-download-archive));
- a compatible cuDNN library (recommemded: v8.4.0 for CUDA-11.x from [cuDNN archive](https://developer.nvidia.com/rdp/cudnn-archive)).

For more info on GPU dependencies please check our [GPU-advice page on DeBCR GitHub](https://github.com/DeBCR/DeBCR/blob/main/docs/GPU-advice.md). 

### Create a package environment (optional)

For a clean isolated installation, we advice using one of Python package environment managers, for example:
- `micromamba`/`mamba` (see [mamba.readthedocs.io](https://mamba.readthedocs.io/))
- `conda-forge` (see [conda-forge.org](https://conda-forge.org/))

Create an environment for `napari-debcr` using
```bash
micromamba env create -n napari-debcr python=3.9 -y
```
and activate it for further installation or usage by
```bash
micromamba activate napari-debcr
```

### Install `napari`

Make sure you have [napari](https://github.com/napari/napari) installed. To install it via [pip](https://pypi.org/project/pip/) use:

```bash
pip install napari[all]
```

### Install napari-debcr

Install one of the `napari-debcr` versions:
- GPU (**recommended**; backend: TensorFlow-GPU-v2.11):
  ```bash
  pip install 'napari-debcr[tf-gpu]'
  ```
- CPU (*limited*; backend: TensorFlow-CPU-v2.11)
  ```bash
  pip install 'napari-debcr[tf-cpu]'
  ```

### Test GPU visibility

For a GPU version installation, it is recommended to check if your GPU device is recognised by **TensorFlow** using
```bash
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

which for a single GPU device should produce a similar output as below:
```
[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

If your GPU device list is empty, please check our [GPU-advice page on DeBCR GitHub](https://github.com/DeBCR/DeBCR/blob/main/docs/GPU-advice.md). 

## Usage

To start using `napari-debcr`,
1. activate `napari-debcr` environment, if was inactive, by
```bash
micromamba activate napari-debcr
```
2. start Napari by typing
```bash
napari
```
3. in Napari window, open `napari-debcr` plugin by clicking in the main menu

`Plugins` &rarr; `DeBCR (DeBCR)`
