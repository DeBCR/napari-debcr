from qtpy.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget, QGroupBox,
)

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

class OutputDataLayout:
    
    def __init__(self, viewer: "napari.viewer.Viewer"):
        self.viewer = viewer
        
        self.layer_out = None
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()
        
        # Layout: Label + ComboBox
        to_layer_layout = QHBoxLayout()
        
        ## Label
        to_layer_label = QLabel("to image stack:")
        to_layer_layout.addWidget(to_layer_label)
        
        ## LineEdit: text field for output layer name
        self.layer_out = QLineEdit()
        to_layer_layout.addWidget(self.layer_out)
        
        to_layer_layout.setStretchFactor(to_layer_label, 0)
        to_layer_layout.setStretchFactor(self.layer_out, 1)
        
        # END Layout: Label + LineEdit
        layout.addLayout(to_layer_layout)
        
        #self.setLayout(layout)
        self.layout = layout
        
    def _update_layer_out(self, text):
       self.layer_out.setText(text)

class OutputDataWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.widget = OutputDataLayout(viewer)
        self.layer_out = self.widget.layer_out
        self.setLayout(self.widget.layout)
    
    def _update_layer_out(self, text):
       self.widget._update_layer_out(text)

class OutputDataGroupBox(QGroupBox):
    def __init__(self, viewer: "napari.viewer.Viewer", title):
        super().__init__(title)
        self.widget = OutputDataLayout(viewer)
        self.layer_out = self.widget.layer_out
        self.setLayout(self.widget.layout)
    
    def _update_layer_out(self, text):
       self.widget._update_layer_out(text)