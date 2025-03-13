import os
import glob

from qtpy.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox,
    QFileDialog, QWidget
)
from qtpy.QtCore import QThread, Signal

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

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

class DeBCRInferenceWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer
        self.log_widget = log_widget
        self._init_layout()
        
        self.debcr = None
        
    def _init_layout(self):
        
        layout = QVBoxLayout()

        ## Groupbox to setup input data
        data_in_group = QGroupBox("Input data")
        
        ## Layout to choose layer as input data
        data_in_layout = QHBoxLayout()
        data_in_label = QLabel("from image layer:")
        data_in_layout.addWidget(data_in_label)
        
        # Drop-down to select layer as input data
        self.layer_select = QComboBox()
        self._update_layer_select()
        self.layer_select.activated.connect(self._update_layer_select) # update drop-down menu
        self.layer_select.currentTextChanged.connect(self._update_text_field) # update output label
        data_in_layout.addWidget(self.layer_select)
        
        data_in_layout.setStretchFactor(data_in_label, 0)
        data_in_layout.setStretchFactor(self.layer_select, 1)
        ## END Layout for input data
        data_in_group.setLayout(data_in_layout)
        ## END Groupbox to setup input data
        layout.addWidget(data_in_group)
        
        ## Groupbox to load model
        weights_group = QGroupBox("Trained model")
        weights_layout = QVBoxLayout()
        
        ### Sublayout for weights directory
        weights_dir = QHBoxLayout()
        weights_dir.addWidget(QLabel("Provide weights path:"))
        
        self.choose_dir_btn = QPushButton("Choose directory")
        self.choose_dir_btn.clicked.connect(self._on_choose_dir_click)
        weights_dir.addWidget(self.choose_dir_btn)
        ### END Sublayout for weights directory
        weights_layout.addLayout(weights_dir)
        
        ### Sublayout for weights file
        weights_file = QHBoxLayout()
        weights_file.addWidget(QLabel("Select weights file:"))
        
        # Drop-down to select weights file
        self.weights_select = QComboBox()
        weights_file.addWidget(self.weights_select)
        ### END Sublayout for model weights file
        weights_layout.addLayout(weights_file)
        
        ### Sublayout to show model weights path
        weights_show_btns = QHBoxLayout()
        
        # Button to show full weights path
        self.show_dir_btn = QPushButton("Show selected path")
        self.show_dir_btn.clicked.connect(self._on_show_sel_dir_click)
        weights_show_btns.addWidget(self.show_dir_btn)

        # Button to show full weights path
        self.show_dir_btn = QPushButton("Show loaded path")
        self.show_dir_btn.clicked.connect(self._on_show_load_dir_click)
        weights_show_btns.addWidget(self.show_dir_btn)
         
        ### END Sublayout to show model weights path
        weights_layout.addLayout(weights_show_btns)

        # Button to load model
        self.load_model_button = QPushButton("Load model") 
        self.load_model_button.clicked.connect(self._on_load_model_click)
        weights_layout.addWidget(self.load_model_button)
        
        weights_group.setLayout(weights_layout)
        ## END Groupbox to load model
        layout.addWidget(weights_group)

        # Layout to setup batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("batch_size:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(16, 128)
        self.batch_spin.setSingleStep(16)
        self.batch_spin.setValue(32) # default
        batch_layout.addWidget(self.batch_spin)
        # END Layout to setup batch size
        layout.addLayout(batch_layout)
        
        ## Groupbox to setup output data
        data_out_group = QGroupBox("Output data")        
        
        ## Layout to choose layer as output data
        data_out_layout = QHBoxLayout()
        
        data_out_label = QLabel("to image layer:")
        data_out_layout.addWidget(data_out_label)
        
        # Text field to name the output image layer 
        self.layer_out = QLineEdit()
        data_out_layout.addWidget(self.layer_out)
        
        data_out_layout.setStretchFactor(data_out_label, 0)
        data_out_layout.setStretchFactor(self.layer_out, 1)
        ## END Layout for output data
        
        data_out_group.setLayout(data_out_layout)
        ## END Groupbox to setup output data
        layout.addWidget(data_out_group)
        
        # Widget to run prediction
        run_widget = QPushButton("Run prediction")
        run_widget.clicked.connect(self._on_run_click)
        self.run_btn = run_widget
        layout.addWidget(run_widget)
        
        layout.addStretch()
        self.setLayout(layout)

        for event in ["inserted", "removed", "moved"]:
            getattr(self.viewer.layers.events, event).connect(lambda e: self._update_layer_select())
        
        # Store a weights dir path
        self.sel_weights_dirpath = None
        self.load_weights_prefix = None

    def _on_choose_dir_click(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Weights Directory")
        
        if dir_path:
            self.sel_weights_dirpath = os.path.abspath(dir_path)
            #self.log_widget.add_log(f'Selected weights directory path:\n{self.sel_weights_dirpath}')
            self._update_weights_dropdown() # update dropdown with found weight files
     
    def _on_show_sel_dir_click(self):
        
        if self.sel_weights_dirpath:
            self.log_widget.add_log(f'Selected weights path:\n{self.sel_weights_dirpath}/{self.weights_select.currentText()}.*')
        else:
            self.log_widget.add_log('No weights directory selected yet.')

    def _on_show_load_dir_click(self):
        
        if self.load_weights_prefix:
            self.log_widget.add_log(f'Loaded weights path:\n{self.load_weights_prefix}.*')
        else:
            self.log_widget.add_log('No model weights loaded yet.')
            
    def _update_weights_dropdown(self):
        self.weights_select.clear()
        
        if not self.sel_weights_dirpath:
            return

        # Find all .index files (checkpoint files)
        weight_filepaths = sorted(glob.glob(f'{self.sel_weights_dirpath}/*.index'))
        
        if weight_filepaths:
            weight_filenames = [os.path.basename(filepath) for filepath in weight_filepaths]
            weight_names = [filename.replace(".index", "") for filename in weight_filenames]
            self.weights_select.addItems(weight_names)
            self.log_widget.add_log('Found model weights!')
        else:
            self.log_widget.add_log(f'No model weights found!\nExpected contents: ckpt-*.index, ckpt-*.data.\nCheck weights directory path...')

    def _update_text_field(self, text):
        if self.layer_out.text() == "":
            self.layer_out.setText(f"{self.layer_select.currentText()}.predict")
    
    def _on_load_model_click(self):
        
        if not self.sel_weights_dirpath:
            self.log_widget.add_log('No weights directory selected yet.')
            return
        
        selected_file = self.weights_select.currentText()

        if not selected_file:
            self.log_widget.add_log(f'No model weight files (ckpt*.index, ckpt*.data) found!\nCheck weights directory path...')
            return

        checkpoint_file_prefix = selected_file.replace(".index", "")
        checkpoint_prefix = str(f'{self.sel_weights_dirpath}/{checkpoint_file_prefix}')
        self.log_widget.add_log(f'Loading weights from: {checkpoint_prefix}')
        
        self.debcr = debcr.model.init(self.sel_weights_dirpath, checkpoint_file_prefix)
        self.load_weights_prefix = checkpoint_prefix
        
        self.log_widget.add_log(f'Weights loaded successfully:\n{self.load_weights_prefix}.*')

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
    
    def _on_run_click(self):

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