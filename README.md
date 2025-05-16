# napari-debcr

<!--
[![License MIT](https://img.shields.io/pypi/l/napari-debcr.svg?color=green)](https://github.com/DeBCR/napari-debcr/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-debcr.svg?color=green)](https://pypi.org/project/napari-debcr)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-debcr.svg?color=green)](https://python.org)
[![tests](https://github.com/DeBCR/napari-debcr/workflows/tests/badge.svg)](https://github.com/DeBCR/napari-debcr/actions)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-debcr)](https://napari-hub.org/plugins/napari-debcr)
-->

[DeBCR] is a deep learning-based tool for light microscopy image deblurring (denoising/deconvolution).

This `debcr-napari` plugin is created to provide a graphical interface for [DeBCR] in [napari]. 

----------------------------------

This [napari] plugin was initialized with [copier] using the [napari-plugin-template].

For the installation/usage questions/issues:
- related to this plugin use the [napari-debcr Issue Tracker](https://github.com/DeBCR/napari-debcr/issues);
- related to the DeBCR toolkit use the [DeBCR Issue Tracker](https://github.com/DeBCR/DeBCR/issues).

This page contains only information on the `napari-debcr` plugin installation. All the further details on the `DeBCR` like:
- deep learning architecture;
- links to the sample data and trained model weights;
- GPU installation-related questions;
and so on are provided on the toolkit Github page: [DeBCR].

## Installation

There are two installation versions for `DeBCR`:
- a GPU version (**recommended**) -  allows full `DeBCR` functionality, including fast model training;
- a CPU version (*limited*) - suitable only if you do not plan to use training, since doing it on CPUs might be very slow.

For a GPU version you need to have access to a GPU device with:
- preferrably at least 16Gb of VRAM;
- a CUDA Toolkit version compatible to your device (recommemded: [CUDA-11.7](https://developer.nvidia.com/cuda-11-7-0-download-archive));
- a cuDNN version compatible to the CUDA above (recommemded: v8.4.0 for CUDA-11.x from [cuDNN archive](https://developer.nvidia.com/rdp/cudnn-archive)).

#### 0. Create a package environment (optional)

For a clean installation, we recommend using one of Python package environment managers, for example:
- `micromamba`/`mamba` (see [mamba.readthedocs.io](https://mamba.readthedocs.io/)), used as example below
- `conda-forge` (see [conda-forge.org](https://conda-forge.org/))

We will use `micromamba` as an example package manager. Create an environment for `DeBCR` using
```bash
micromamba env create -n debcr python=3.9
```
and activate it for further installation or usage by
```bash
micromamba activate debcr
```

#### 1. Install `napari`

Make sure you have [napari] installed. To install `napari` via [pip] use:

```bash
    pip install napari[all]
```

#### 2. Install `napari-debcr`

<!--
```bash
    pip install napari-debcr
```
-->

To install `napari-debcr` plugin for [DeBCR] you need to clone this repository and install the plugin locally.

Clone this repository to the desired location and enter clone folder
```bash
cd /path/for/clone
git clone https://github.com/DeBCR/napari-debcr
cd ./DeBCR
```

and install one of the `napari-debcr` versions as

| Target hardware  | Backend         | Command  |
| :--------------- | :-------------- | :------- | 
| GPU (**recommended**) | TensorFlow-GPU-2.11 | <pre> pip install -e .[tf-gpu] </pre> |
| CPU (*limited*) | TensorFlow-CPU-2.11 | <pre> pip install -e .[tf-cpu] </pre> |

For a GPU version installation, it is recommended to check if your GPU device is recognised by **TensorFlow** using
```bash
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

which for a single GPU device should produce a similar output as below:
```
[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

If your GPU device list is empty, please check our tips from [DeBCR] repository on [GPU-advice page](https://github.com/DeBCR/DeBCR/docs/GPU-advice.md).

<!--
## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.
-->

## License

Distributed under the terms of the [MIT] license,
"napari-debcr" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[@napari]: https://github.com/napari
[napari]: https://github.com/napari/napari
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[copier]: https://copier.readthedocs.io/en/stable/
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/

[MIT]: http://opensource.org/licenses/MIT

[DeBCR]: https://github.com/DeBCR/DeBCR
[file an issue]: https://github.com/DeBCR/napari-debcr/issues