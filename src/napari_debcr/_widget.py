import os
import glob

from qtpy.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QTextEdit, QLabel,
    QPushButton, QComboBox,
    QFileDialog, QWidget
)

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

import debcr
    
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

        # Button to run prediction
        run_widget = QPushButton("Click me!")
        run_widget.clicked.connect(self._on_run_click)
        self.run_btn = run_widget

        ## Layout for input data
        data_layout = QVBoxLayout()
        data_layout.addWidget(QLabel("Select input data:"))

        # Drop-down to select layer as input data
        self.layer_select = QComboBox()
        self._update_layer_select()
        self.layer_select.activated.connect(self._update_layer_select)
        data_layout.addWidget(self.layer_select)
        ## END Layout for input data
        
        ## Layout for model weights
        weights_layout = QVBoxLayout()
        
        ### Sublayout for model weights directory
        weights_dir_layout = QHBoxLayout()

        self.choose_dir_btn = QPushButton("Choose directory")
        self.choose_dir_btn.clicked.connect(self._on_choose_dir_click)
        weights_dir_layout.addWidget(self.choose_dir_btn)
        
        self.show_dir_btn = QPushButton("Show path")
        self.show_dir_btn.clicked.connect(self._on_show_dir_click)
        weights_dir_layout.addWidget(self.show_dir_btn)
        ### END Sublayout for model weights directory
        
        ### Sublayout for model weights file
        weights_file_layout = QHBoxLayout()
        
        # Drop-down to select weights file
        self.weights_select = QComboBox()
        weights_file_layout.addWidget(self.weights_select)

        # Button to load weights file
        self.load_button = QPushButton("Load weights") 
        self.load_button.clicked.connect(self._on_weights_load_click)
        weights_file_layout.addWidget(self.load_button)
        ### END Sublayout for model weights file

        weights_layout.addWidget(QLabel("Provide weights directory:"))
        weights_layout.addLayout(weights_dir_layout)
        weights_layout.addWidget(QLabel("Select weights file:"))
        weights_layout.addLayout(weights_file_layout)
        ## END Layout for model weights

        # Button to print model info
        model_info_widget = QPushButton("Show model info")
        model_info_widget.clicked.connect(self._on_model_info_click)
        self.model_info_btn = model_info_widget
        
        # Log box for messages for user
        log_widget = QTextEdit()
        log_widget.setReadOnly(True)
        self.log_box = log_widget
        
        # General plugin layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addLayout(data_layout)
        layout.addLayout(weights_layout)
        layout.addWidget(model_info_widget)
        layout.addWidget(run_widget)
        layout.addWidget(log_widget)
                
        # Store a weights dir path
        self.current_weights_dir = None
    
    def _on_run_click(self):
        self._log_message("Model will be runned!")
    
    def _on_model_info_click(self):
        self.debcr.summary(print_fn=self._log_message)
    
    def _on_choose_dir_click(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Weights Directory")
        
        if dir_path:
            self.current_weights_dir = os.path.abspath(dir_path)
            self._update_weights_dropdown() # update dropdown with found weight files
            self._log_message(f'Selected weights directory path:\n{self.current_weights_dir}')
     
    def _on_show_dir_click(self):
        
        if self.current_weights_dir:
            self._log_message(f'Selected weights directory path:\n{self.current_weights_dir}')
        else:
            self._log_message('No weights directory selected yet.')
    
    def _update_weights_dropdown(self):
        self.weights_select.clear()
        
        if not self.current_weights_dir:
            return

        # Find all .index files (checkpoint files)
        weight_filepaths = sorted(glob.glob(f'{self.current_weights_dir}/*.index'))
        
        if weight_filepaths:
            weight_filenames = [os.path.basename(filepath) for filepath in weight_filepaths]
            weight_names = [filename.replace(".index", "") for filename in weight_filenames]
            self.weights_select.addItems(weight_names)
        else:
            self.weights_select.addItem("No checkpoint files found.")

    def _on_weights_load_click(self):
        
        if not self.current_weights_dir:
            self._log_message('No weights directory selected yet.')
            return
        
        selected_file = self.weights_select.currentText()

        if selected_file == "No checkpoint files found" or not selected_file:
            self._log_message('No valid file selected.')
            return

        checkpoint_file_prefix = selected_file.replace(".index", "")
        checkpoint_prefix = str(f'{self.current_weights_dir}/{checkpoint_file_prefix}')
        self._log_message(f'Loading weights from: {checkpoint_prefix}')

        self.debcr = debcr.model.load(self.current_weights_dir, checkpoint_file_prefix)

        self._log_message('Weights loaded successfully!')
        
    def _log_message(self, message):
        self.log_box.append(f'\n{message}')
    
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