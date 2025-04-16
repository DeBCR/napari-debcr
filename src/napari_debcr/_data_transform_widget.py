from qtpy.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit,
    QPushButton, QSpinBox,
    QWidget
)
from qtpy.QtCore import QThread, Signal

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

from ._input_data_widget import InputDataGroupBox
from ._output_data_widget import OutputDataGroupBox

import debcr

class DataTransformThread(QThread):
    finished_signal = Signal()  # Signal to notify when finished
    log_signal = Signal(str) # Signal for log messages
    result_signal = Signal(object, str)  # Signal to pass prediction results (image data, name)
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
    
    def run(self):
        
        input_name = self.widget.layer_select.currentText()
        input_data = None
        
        for layer in self.widget.viewer.layers:
            if isinstance(layer, napari.layers.Image) and (layer.name == input_name) and (layer.data is not None):
                input_data = layer.data
                break
        
        if input_data is None:
            self.log_signal.emit('No input data is loaded!')
            self.log_signal.emit('Preprocessing is aborted.')
            self.finished_signal.emit()
            return
        
        self.log_signal.emit(f'Preprocessing {input_name}')
        
        data_prep = debcr.data.prepare(input_data, patch_size = self.widget.patch_size)
        output_name = self.widget.layer_out.text()
        self.result_signal.emit(data_prep, output_name)
        
        self.log_signal.emit(f'New data shape: {data_prep.shape}')
        self.log_signal.emit(f'Preprocessing is finished: {output_name}')
        
        self.finished_signal.emit()  # Notify UI when done

class DataTransformWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer
        self.log_widget = log_widget

        self.layer_select = None
        self.layer_out = None
        self.patch_size = 128 # default
        self.debcr = None
        
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()
         
        # Groupbox: input data
        data_in_widget = InputDataGroupBox(self.viewer, "Input")
        self.layer_select = data_in_widget.layer_select
        layout.addWidget(data_in_widget)
        
        # Groupbox: output data
        data_out_widget = OutputDataGroupBox(self.viewer, "Output")
        self.layer_out = data_out_widget.layer_out
        layout.addWidget(data_out_widget)
        
        # update output label upon input label change 
        self.layer_select.currentTextChanged.connect(lambda: data_out_widget._update_layer_out(f"{self.layer_select.currentText()}.prep"))

        # Groupbox: settings
        params_group = QGroupBox("Settings")
        params_layout = QVBoxLayout()

        #########
        # Layout: patch size
        patch_layout = QHBoxLayout()
        patch_layout.addWidget(QLabel("patch size (X/Y):"))
        self.patch_spin = QSpinBox()
        self.patch_spin.setRange(32, 256)
        self.patch_spin.setSingleStep(16)
        self.patch_spin.setValue(self.patch_size) # default
        self.patch_spin.valueChanged.connect(self._update_patch_size)
        patch_layout.addWidget(self.patch_spin)
        # END Layout: patch size
        #########
        params_layout.addLayout(patch_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Widget to run data transform
        run_widget = QPushButton("Run transform")
        run_widget.clicked.connect(self._on_run_click)
        self.run_btn = run_widget
        layout.addWidget(run_widget)
        
        layout.addStretch()
        self.setLayout(layout)

    def _update_patch_size(self, value):
        self.patch_size = value
           
    def _on_run_click(self):
        self._toggle_run_btn(False)
        # Run preprocessing in a background thread
        self.thread = PreprocessThread(self)
        self.thread.log_signal.connect(self.log_widget.add_log)
        self.thread.result_signal.connect(self._add_result_layer)
        self.thread.finished_signal.connect(lambda: self._toggle_run_btn(True))
        self.thread.start()

    def _add_result_layer(self, image_data, image_name):
        self.viewer.add_image(image_data, name=image_name)
    
    def _toggle_run_btn(self, enabled):
        if enabled:
            self.run_btn.setText("Run transform")
            self.run_btn.setEnabled(True)
        else:
            self.run_btn.setText("Running...")
            self.run_btn.setEnabled(False)
            QApplication.processEvents()