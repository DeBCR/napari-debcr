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
from ._load_weights_widget import LoadWeightsGroupBox
from ._output_data_widget import OutputDataGroupBox

import debcr

class PredictionThread(QThread):
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
            self.finished_signal.emit()
            return
        
        self.log_signal.emit(f'Running prediction on {input_name}')
        
        data_pred = debcr.model.predict(eval_model=self.widget.debcr, input_data=input_data, batch_size=self.widget.batch_spin.value())
        output_name = self.widget.layer_out.text()
        
        self.result_signal.emit(data_pred, output_name)
        self.log_signal.emit(f'Prediction is finished: {output_name}')
        
        self.finished_signal.emit()  # Notify UI when done

class PredictionWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer
        self.log_widget = log_widget

        self.layer_select = None
        self.layer_out = None
        self.debcr = None
        
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()
         
        # Groupbox: input data
        data_in_widget = InputDataGroupBox(self.viewer, "Input")
        self.layer_select = data_in_widget.layer_select
        layout.addWidget(data_in_widget)

        # Groupbox: trained model
        weigths_widget = LoadWeightsGroupBox(self.viewer, "Trained model", self.log_widget)
        layout.addWidget(weigths_widget)
        
        ## Groupbox: parameters
        params_group = QGroupBox("Settings")
        params_layout = QVBoxLayout()
        
        # Layout to setup batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("batch load size:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 128)
        self.batch_spin.setSingleStep(8)
        self.batch_spin.setValue(32) # default
        batch_layout.addWidget(self.batch_spin)
        # END Layout to setup batch size
        params_layout.addLayout(batch_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Groupbox: output data
        data_out_widget = OutputDataGroupBox(self.viewer, "Output")
        self.layer_out = data_out_widget.layer_out
        layout.addWidget(data_out_widget)
        
        # update output label upon input label change 
        self.layer_select.currentTextChanged.connect(lambda: data_out_widget._update_layer_out(f"{self.layer_select.currentText()}.pred"))
        
        # Widget to run prediction
        run_widget = QPushButton("Run prediction")
        run_widget.clicked.connect(lambda: self._on_run_click(weigths_widget.debcr))
        self.run_btn = run_widget
        layout.addWidget(run_widget)
        
        layout.addStretch()
        self.setLayout(layout)
       
    def _on_run_click(self, model):

        self.debcr = model
        if self.debcr is None:
            self.log_widget.add_log(f'No model weights loaded yet!')
            return
        
        self._toggle_run_btn(False)
        
        # Run prediction in a background thread
        self.thread = PredictionThread(self)
        self.thread.log_signal.connect(self.log_widget.add_log)
        self.thread.result_signal.connect(self._add_result_layer)
        self.thread.finished_signal.connect(lambda: self._toggle_run_btn(True))
        self.thread.start()

    def _add_result_layer(self, image_data, image_name):
        self.viewer.add_image(image_data, name=image_name)
    
    def _toggle_run_btn(self, enabled):
        if enabled:
            self.run_btn.setText("Run prediction")
            self.run_btn.setEnabled(True)
        else:
            self.run_btn.setText("Running prediction...")
            self.run_btn.setEnabled(False)
            QApplication.processEvents()