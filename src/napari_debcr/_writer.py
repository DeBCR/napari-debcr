import os
import numpy as np

from typing import Callable, List, Any, Literal, Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import napari

DataType = Any
LayerAttributes = dict
LayerName = Literal["image"]
FullLayerData = Tuple[DataType, LayerAttributes, LayerName]
NpzFileWriter = Callable[[str, FullLayerData], List[str]]

def npz_file_writer(path: str, layers_data: FullLayerData) -> List[str]:

    layer_data = layers_data[0]
    image_data = np.asarray(layer_data[0])
    np.savez(path, data=image_data)
    
    return [path]