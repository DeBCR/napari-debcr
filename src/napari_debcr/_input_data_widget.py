from qtpy.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel,
    QComboBox,
    QWidget, QGroupBox,
)

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

class InputDataLayout:
    
    def __init__(self, viewer: "napari.viewer.Viewer"):
        self.viewer = viewer
        
        self.layer_select = None
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()
        
        # Layout: Label + ComboBox
        from_layer_layout = QHBoxLayout()
        
        ## Label
        from_layer_label = QLabel("from layer:")
        from_layer_layout.addWidget(from_layer_label)
        
        ## ComboBox: to select image layer
        self.layer_select = QComboBox()
        self._update_layer_select()
        self.layer_select.activated.connect(self._update_layer_select) # update drop-down menu
        from_layer_layout.addWidget(self.layer_select)
        
        from_layer_layout.setStretchFactor(from_layer_label, 0)
        from_layer_layout.setStretchFactor(self.layer_select, 1)
        
        # END Layout: Label + ComboBox
        layout.addLayout(from_layer_layout)
        
        #self.setLayout(layout)
        self.layout = layout

        for event in ["inserted", "removed", "moved"]:
            getattr(self.viewer.layers.events, event).connect(lambda e: self._update_layer_select())

    def _update_layer_select(self):
        
        current_layer = self.layer_select.currentText()
        self.layer_select.clear()

        layer_names = []
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.Image):
                self.layer_select.addItem(layer.name)
                layer_names.append(layer.name)
        
        if current_layer in layer_names:
            self.layer_select.setCurrentText(current_layer)
        elif layer_names:
            self.layer_select.setCurrentIndex(0)

class InputDataWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.widget = InputDataLayout(viewer)
        self.layer_select = self.widget.layer_select
        self.setLayout(self.widget.layout)

class InputDataGroupBox(QGroupBox):
    def __init__(self, viewer: "napari.viewer.Viewer", title):
        super().__init__(title)
        self.widget = InputDataLayout(viewer)
        self.layer_select = self.widget.layer_select
        self.setLayout(self.widget.layout)