from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, Container, create_widget
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QLabel, QFileDialog, QWidget
import napari
from skimage.util import img_as_float

import debcr

if TYPE_CHECKING:
    import napari

class InferenceQWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.viewer.layers.events.inserted.connect(
            lambda e: self._update_layer_select())
        self.viewer.layers.events.removed.connect(
            lambda e: self._update_layer_select())
        self.viewer.layers.events.moved.connect(
            lambda e: self._update_layer_select())
        self._init_layout()
        self.debcr = debcr.model.load()
        
    def _init_layout(self):

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)
        self.run_btn = btn
        
        input_data_line = QHBoxLayout()
        input_data_line.addWidget(QLabel("Select input data:"))
        self.layer_select = QComboBox()
        self._update_layer_select()
        self.layer_select.activated.connect(self._update_layer_select)
        input_data_line.addWidget(self.layer_select)

        weight_file_line = QHBoxLayout()
        weight_file_line.addWidget(QLabel("Load weights: "))
        self.weight_file_button = QPushButton("Open")
        self.weight_file_button.clicked.connect(self._on_weight_file_click)
        weight_file_line.addWidget(self.weight_file_button)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addLayout(input_data_line)
        layout.addLayout(weight_file_line)
        layout.addWidget(btn)
    
    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")
        print("selected layer is", len(self.layer_select.currentText()))
        print("loaded model info is ", self.debcr.summary())

    def _on_weight_file_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load weights (ckpt-*.index file)", "",
            "All Files (*);;TensorFlow Files (*.index)",
            options=options)
        if file_name:
            print(file_name)
            debcr.load_weights()
            #self.ufish.load_weights(file_name) # load weights via DeBCR API here!
            
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

# if we want even more control over our widget, we can use
# magicgui `Container`
class ImageThreshold(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        # use create_widget to generate widgets from type annotations
        self._image_layer_combo = create_widget(
            label="Image", annotation="napari.layers.Image"
        )
        self._threshold_slider = create_widget(
            label="Threshold", annotation=float, widget_type="FloatSlider"
        )
        self._threshold_slider.min = 0
        self._threshold_slider.max = 1
        # use magicgui widgets directly
        self._invert_checkbox = CheckBox(text="Keep pixels below threshold")

        # connect your own callbacks
        self._threshold_slider.changed.connect(self._threshold_im)
        self._invert_checkbox.changed.connect(self._threshold_im)

        # append into/extend the container with your widgets
        self.extend(
            [
                self._image_layer_combo,
                self._threshold_slider,
                self._invert_checkbox,
            ]
        )

    def _threshold_im(self):
        image_layer = self._image_layer_combo.value
        if image_layer is None:
            return

        image = img_as_float(image_layer.data)
        name = image_layer.name + "_thresholded"
        threshold = self._threshold_slider.value
        if self._invert_checkbox.value:
            thresholded = image < threshold
        else:
            thresholded = image > threshold
        if name in self._viewer.layers:
            self._viewer.layers[name].data = thresholded
        else:
            self._viewer.add_labels(thresholded, name=name)
