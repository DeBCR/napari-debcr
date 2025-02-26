# napari-debcr

[![License MIT](https://img.shields.io/pypi/l/napari-debcr.svg?color=green)](https://github.com/DeBCR/napari-debcr/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-debcr.svg?color=green)](https://pypi.org/project/napari-debcr)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-debcr.svg?color=green)](https://python.org)
<!--
[![tests](https://github.com/DeBCR/napari-debcr/workflows/tests/badge.svg)](https://github.com/DeBCR/napari-debcr/actions)
-->
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-debcr)](https://napari-hub.org/plugins/napari-debcr)

[debcr] is a deep learning-based tool for image deblurring (denoising/deconvolution). It is primarily intended to be used for light microscopy data.

This `debcr-napari` plugin is created to provide a simple graphical interface to use a lightweight CPU version of [debcr] for deblurred image predictions in [napari]. 

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

## Installation

1. Make sure you have [napari] installed. To install `napari` via [pip] use:

```bash
    pip install napari[all]
```

2. Install `napari-debcr` plugin for [DeBCR] via [pip]:

```bash
    pip install git+https://github.com/DeBCR/napari-debcr.git
```

<!--
```bash
    pip install napari-debcr
```
-->

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

[debcr]: https://github.com/DeBCR/DeBCR
[file an issue]: https://github.com/DeBCR/napari-debcr/issues