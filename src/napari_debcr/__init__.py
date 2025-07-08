from importlib.metadata import version

__version__ = version("napari-debcr")

from ._reader import get_reader
from ._writer import npz_file_writer
#from ._sample_data import make_sample_data
from ._plugin import DeBCRPlugin

__all__ = (
    "get_reader",
    "npz_file_writer",
#    "make_sample_data",
    "DeBCRPlugin"
)
