import os
import glob

from qtpy.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QFileDialog,
)

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

import debcr

class ModelConfigsGroupBox(QGroupBox):
    
    def __init__(self, viewer: "napari.viewer.Viewer", title: str, log_widget):
        super().__init__(title)
        
        self.viewer = viewer
        self.log_widget = log_widget
        
        self.config = debcr.config.load()
        
        self._init_layout()
            
    def _init_layout(self):
        
        layout = QVBoxLayout()
        
        #########
        # Layout: batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("batch load size:"))
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(16, 128)
        self.batch_spin.setSingleStep(16)
        self.batch_spin.setValue(self.config['batch_size']) # default
        self.batch_spin.valueChanged.connect(lambda val: self._on_value_changed(val, 'batch_size'))
        batch_layout.addWidget(self.batch_spin)
        # END Layout: batch size
        #########
        layout.addLayout(batch_layout)

        #########
        # Layout: number of training steps
        steps_layout = QHBoxLayout()
        steps_layout.addWidget(QLabel("training steps:"))
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(10, 10000)
        self.steps_spin.setSingleStep(10)
        self.steps_spin.setValue(self.config['NUM_STEPS']) # default
        self.steps_spin.valueChanged.connect(lambda val: self._on_value_changed(val, 'NUM_STEPS'))
        steps_layout.addWidget(self.steps_spin)
        # END Layout: number of training steps
        #########
        layout.addLayout(steps_layout)

        #########
        # Layout: training patience
        patience_layout = QHBoxLayout()
        patience_layout.addWidget(QLabel("patience:"))
        self.patience_spin = QSpinBox()
        self.patience_spin.setRange(1, 1000)
        self.patience_spin.setSingleStep(5)
        self.patience_spin.setValue(self.config['patience']) # default
        self.patience_spin.valueChanged.connect(lambda val: self._on_value_changed(val, 'patience'))
        patience_layout.addWidget(self.patience_spin)
        # END Layout: training patience
        #########
        layout.addLayout(patience_layout)

        #########
        # Layout: learning rate
        lr_layout = QHBoxLayout()
        lr_layout.addWidget(QLabel("learning rate:"))
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setDecimals(5)
        self.lr_spin.setRange(0, 1)
        self.lr_spin.setSingleStep(0.001)
        self.lr_spin.setValue(self.config['learning_rate']) # default
        self.lr_spin.valueChanged.connect(lambda val: self._on_value_changed(val, 'learning_rate'))
        lr_layout.addWidget(self.lr_spin)
        # END Layout: learning rate
        #########
        layout.addLayout(lr_layout)

        #########
        # Layout: defaults / save
        btn_layout = QHBoxLayout()
        
        ## Button: restore defaults
        self.defaults_btn = QPushButton("Restore defaults")
        self.defaults_btn.clicked.connect(self._on_defaults_click)
        btn_layout.addWidget(self.defaults_btn)

        ## Button: load from file
        self.save_btn = QPushButton("Load From File")
        self.save_btn.clicked.connect(self._on_load_config_click)
        btn_layout.addWidget(self.save_btn)
        
        ## Button: save to file
        self.save_btn = QPushButton("Save To File")
        self.save_btn.clicked.connect(self._on_save_config_click)
        btn_layout.addWidget(self.save_btn)
        # END Layout: defaults / save
        #########
        layout.addLayout(btn_layout)
        
        #########
        # Layout: model output dirpath
        outdir_layout = QHBoxLayout()
        outdir_layout.addWidget(QLabel("Model output:"))
        
        ## TextField: type path
        self.outdir_field = QLineEdit()
        self.outdir_field.setText(self.config['weights_path'])
        self.outdir_field.textChanged.connect(self._on_text_changed)
        outdir_layout.addWidget(self.outdir_field)
        
        ## Button: set path
        self.set_outdir_btn = QPushButton("Choose directory")
        self.set_outdir_btn.clicked.connect(self._on_set_outdir_click)
        outdir_layout.addWidget(self.set_outdir_btn)
        # END Layout: model output dirpath
        #########
        layout.addLayout(outdir_layout)
        
        self.setLayout(layout)
        self.layout = layout

    def _on_load_config_click(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration File From...",
            "config.yaml",
            "Text Files (*.yaml);;All Files (*)"
        )
        if path:
            try:
                self._update_config(debcr.config.load(path))
                self.log_widget.add_log(f"Configuration loaded from: {path}")
            except Exception as e:
                self.log_widget.add_log(f"Failed to load configuration: {e}")
    
    def _on_save_config_click(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration File As...",
            "config.yaml",
            "Text Files (*.yaml);;All Files (*)"
        )
        if path:
            debcr.config.save(self.config, path)
            self.log_widget.add_log(f"Configuration saved to: {path}")
        
    def _on_defaults_click(self):
        self._update_config(debcr.config.load())
        
    def _update_config(self, config):
        weights_path = self.config['weights_path']
        self.config = config
        self.config['weights_path'] = weights_path
        
        self.batch_spin.setValue(config['batch_size'])
        self.steps_spin.setValue(config['NUM_STEPS'])
        self.patience_spin.setValue(config['patience'])
        self.lr_spin.setValue(config['learning_rate'])
        
    def _on_text_changed(self, text):
        self.config['weights_path'] = text
        
    def _on_value_changed(self, value, config_param):
        self.config[config_param] = value
    
    def _on_set_outdir_click(self):
        chosen_path = QFileDialog.getExistingDirectory(self, "Choose Model Output Directory")
        if chosen_path:
            self.config['weights_path'] = os.path.abspath(chosen_path)
            self.outdir_field.setText(self.config['weights_path'])