import os
import glob

from qtpy.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit,
    QPushButton, QCheckBox, QSpinBox,
    QComboBox, QGroupBox,
    QWidget,
    QFileDialog,
)

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

import debcr

class LoadWeightsGroupBox(QGroupBox):
    
    def __init__(self, viewer: "napari.viewer.Viewer", title: str, log_widget, add_init_ckbox: bool = False):
        super().__init__(title)
        
        self.viewer = viewer
        self.log_widget = log_widget
        
        self.ckpt_select = None
        self.weights_set_path = None
        self.weights_load_pref = None
        
        self.debcr = None
        self.input_size = 128
        
        self.add_init_ckbox = add_init_ckbox
        
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()

        #########
        # Layout: model input size
        input_size_layout = QHBoxLayout()
        input_size_layout.addWidget(QLabel("model input size:"))
        self.input_size_spin = QSpinBox()
        self.input_size_spin.setRange(32, 256)
        self.input_size_spin.setSingleStep(16)
        self.input_size_spin.setValue(self.input_size) # default
        self.input_size_spin.valueChanged.connect(self._update_input_size)
        input_size_layout.addWidget(self.input_size_spin)
        # END Layout: model input size
        #########
        layout.addLayout(input_size_layout)
        
        if self.add_init_ckbox:
            # Button: init new model
            self.init_ckbox = QCheckBox("initialize new model")
            self.init_ckbox.setChecked(True)
            self.init_ckbox.stateChanged.connect(self._toggle_group)
            layout.addWidget(self.init_ckbox)
        
        #########
        # Layout: weights directory
        weigths_dir_layout = QHBoxLayout()
        weigths_dir_layout.addWidget(QLabel("weights folder:"))
        
        ## TextField: type weights dirpath
        self.weights_dir_field = QLineEdit()
        self.weights_dir_field.setText('./weights')
        self.weights_dir_field.textChanged.connect(self._on_text_changed)
        weigths_dir_layout.addWidget(self.weights_dir_field)
        
        ## Button: set weights dirpath
        self.set_dir_btn = QPushButton("Choose")
        self.set_dir_btn.clicked.connect(self._on_set_dir_click)
        weigths_dir_layout.addWidget(self.set_dir_btn)
        # END Layout: weights directory
        #########
        layout.addLayout(weigths_dir_layout)
        
        #########
        # Layout: checkpoint
        ckpt_layout = QHBoxLayout()
        ckpt_layout.addWidget(QLabel("weights file:"))

        ## Drop-down: select checkpoint
        self.ckpt_select = QComboBox()
        ckpt_layout.addWidget(self.ckpt_select)
        # END Layout: checkpoint
        #########
        layout.addLayout(ckpt_layout)

        if self.add_init_ckbox:
            # Triger to switch off weights setup
            self._toggle_group()
        
        # Button: load model
        self.load_model_btn = QPushButton("(Re)load model") 
        self.load_model_btn.clicked.connect(self._on_load_model_click)
        layout.addWidget(self.load_model_btn)

        self.setLayout(layout)
        self.layout = layout

    def _update_input_size(self, value):
        self.input_size = value
        
    def _toggle_group(self):
        if self.add_init_ckbox:
            enable = not self.init_ckbox.isChecked()
            self.set_dir_btn.setEnabled(enable)
            self.weights_dir_field.setEnabled(enable)
            self.ckpt_select.setEnabled(enable)
        
    def _on_set_dir_click(self):
        chosen_path = QFileDialog.getExistingDirectory(self, "Choose Weights Directory")
        if chosen_path:
            self.weights_set_path = os.path.abspath(chosen_path)
            self.weights_dir_field.setText(self.weights_set_path)
            self._update_ckpt_dropdown() # update dropdown with found weight files

    def _on_text_changed(self, chosen_path):
        if chosen_path:
            self.weights_set_path = os.path.abspath(chosen_path)
            self._update_ckpt_dropdown() # update dropdown with found weight files
    
    def _update_ckpt_dropdown(self):
        self.ckpt_select.clear()
        
        if not self.weights_set_path:
            return

        # Find all .index files (checkpoint files)
        ckpt_filepaths = sorted(glob.glob(f'{self.weights_set_path}/*.index'))
        
        if ckpt_filepaths:
            ckpt_filenames = [os.path.basename(filepath) for filepath in ckpt_filepaths]
            ckpt_names = [filename.replace(".index", "") for filename in ckpt_filenames]
            self.ckpt_select.addItems(ckpt_names)
            self.log_widget.add_log('Found model weights!')
        else:
            self.log_widget.add_log(f'No model weights found!\nExpected: ckpt-*.index, ckpt-*.data')
    
    def _on_load_model_click(self):

        if self.add_init_ckbox and self.init_ckbox.isChecked():
            self.debcr = debcr.model.init(input_size = self.input_size)
            self.log_widget.add_log('Model initialized!')
            print(f'Model summary:{self.debcr.summary()}')
            return
        
        if not self.weights_set_path:
            self.log_widget.add_log('No weights directory selected yet.')
            return
        
        selected_file = self.ckpt_select.currentText()

        if not selected_file:
            self.log_widget.add_log(f'No model weight files (ckpt*.index, ckpt*.data) found!\nCheck weights directory path...')
            return

        checkpoint_file_prefix = selected_file.replace(".index", "")
        checkpoint_prefix = str(f'{self.weights_set_path}/{checkpoint_file_prefix}')
        
        self.debcr = debcr.model.init(weights_path=self.weights_set_path, input_size=self.input_size, ckpt_name=checkpoint_file_prefix)
        self.log_widget.add_log('Model loaded!')
        print(f'Model summary:{self.debcr.summary()}')

        self.weights_load_pref = checkpoint_prefix