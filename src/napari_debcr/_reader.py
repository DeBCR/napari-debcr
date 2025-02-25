import os
import numpy as np

from typing import Union, Sequence, Callable, List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  import napari

PathOrPaths = Union[str, Sequence[str]]
ReaderFunction = Callable[[PathOrPaths], List['napari.types.LayerData']]

def get_reader(path: "PathOrPaths") -> Optional["ReaderFunction"]:
    
    if isinstance(path, str) and path.endswith(".npz"):
        return npz_file_reader
    
    return None


def npz_file_reader(path: "PathOrPaths") -> List["LayerData"]:
    
    data = np.load(path)

    filename,_ = os.path.splitext( os.path.basename(path) )
    layerdata = [
        (data[arrname], {"name": f'{filename}.{arrname}'}, 'image')
        for arrname in data.files
    ]
    
    return layerdata