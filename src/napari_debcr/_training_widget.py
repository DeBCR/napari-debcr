import os
import glob

from qtpy.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit,
    QPushButton, QComboBox,
    QButtonGroup, QRadioButton,
    QSpinBox, QDoubleSpinBox, QCheckBox,
    QFileDialog, QWidget
)
from qtpy.QtCore import QThread, Signal, Qt

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

import debcr

class TrainingThread(QThread):
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
        
        self.result_signal.emit(data_pred, output_name)
        self.log_signal.emit(f'Prediction is finished: {output_name}')
        
        self.finished_signal.emit()  # Notify UI when done

class LayerSelectors:
    def __init__(self):
        self.train_in = None
        self.train_gt = None
        self.val_in = None
        self.val_gt = None

class DeBCRTrainingWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer

        self.layer_select = LayerSelectors()
        self.log_widget = log_widget
        self._init_layout()

        self.debcr = None
        
    def _init_layout(self):
        
        layout = QVBoxLayout()

        ## Groupbox to setup input training data
        data_in_group = QGroupBox("Input data (training)")
        
        ## Layout to choose layer as input training data
        data_in_layout = QHBoxLayout()
        data_in_label = QLabel("from image layer:")
        data_in_layout.addWidget(data_in_label)
        
        # Drop-down to select layer as input training data
        self.layer_select.train_in = QComboBox()
        self._update_layer_select(self.layer_select.train_in)
        self.layer_select.train_in.activated.connect(lambda: self._update_layer_select(self.layer_select.train_in)) # update drop-down menu
        data_in_layout.addWidget(self.layer_select.train_in)
        
        data_in_layout.setStretchFactor(data_in_label, 0)
        data_in_layout.setStretchFactor(self.layer_select.train_in, 1)
        ## END Layout for input training data
        data_in_group.setLayout(data_in_layout)
        ## END Groupbox to setup input training data
        layout.addWidget(data_in_group)

        ## Groupbox to setup GT training data
        data_gt_group = QGroupBox("Ground-truth data (training)")
        
        ## Layout to choose layer as GT training data
        data_gt_layout = QHBoxLayout()
        data_gt_label = QLabel("from image layer:")
        data_gt_layout.addWidget(data_gt_label)
        
        # Drop-down to select layer as GT training data
        self.layer_select.train_gt = QComboBox()
        self._update_layer_select(self.layer_select.train_gt)
        self.layer_select.train_gt.activated.connect(lambda: self._update_layer_select(self.layer_select.train_gt)) # update drop-down menu
        data_gt_layout.addWidget(self.layer_select.train_gt)
        
        data_gt_layout.setStretchFactor(data_gt_label, 0)
        data_gt_layout.setStretchFactor(self.layer_select.train_gt, 1)
        ## END Layout for GT training data
        data_gt_group.setLayout(data_gt_layout)
        ## END Groupbox to setup GT training data
        layout.addWidget(data_gt_group)



        ## Groupbox to setup input validation data
        data_in_val_group = QGroupBox("Input data (validation)")
        
        ## Layout to choose layer as input validation data
        data_in_val_layout = QHBoxLayout()
        data_in_val_label = QLabel("from image layer:")
        data_in_val_layout.addWidget(data_in_val_label)
        
        # Drop-down to select layer as input validation data
        self.layer_select.val_in = QComboBox()
        self._update_layer_select(self.layer_select.val_in)
        self.layer_select.val_in.activated.connect(lambda: self._update_layer_select(self.layer_select.val_in)) # update drop-down menu
        data_in_val_layout.addWidget(self.layer_select.val_in)
        
        data_in_val_layout.setStretchFactor(data_in_val_label, 0)
        data_in_val_layout.setStretchFactor(self.layer_select.val_in, 1)
        ## END Layout for input validation data
        data_in_val_group.setLayout(data_in_val_layout)
        ## END Groupbox to setup input validation data
        layout.addWidget(data_in_val_group)

        

        ## Groupbox to setup GT validation data
        data_gt_val_group = QGroupBox("Ground-truth data (validation)")
        
        ## Layout to choose layer as GT validation data
        data_gt_val_layout = QHBoxLayout()
        data_gt_val_label = QLabel("from image layer:")
        data_gt_val_layout.addWidget(data_gt_val_label)
        
        # Drop-down to select layer as GT validation data
        self.layer_select.val_gt = QComboBox()
        self._update_layer_select(self.layer_select.val_gt)
        self.layer_select.val_gt.activated.connect(lambda: self._update_layer_select(self.layer_select.val_gt)) # update drop-down menu
        data_gt_val_layout.addWidget(self.layer_select.val_gt)
        
        data_gt_val_layout.setStretchFactor(data_gt_val_label, 0)
        data_gt_val_layout.setStretchFactor(self.layer_select.val_gt, 1)
        ## END Layout for GT validation data
        data_gt_val_group.setLayout(data_gt_val_layout)
        ## END Groupbox to setup GT validation data
        layout.addWidget(data_gt_val_group)

        

        
        ## Groupbox to setup validation data
        data_val_group = QGroupBox("Validation data")
        data_val_layout = QVBoxLayout()

        # Buttongroup to setup validation data
        self.radio_group = QButtonGroup(self)
        
        # Layout from split ratio
        # Radio Button + Double Spin Box
        data_val_from_split_layout = QHBoxLayout()
        data_val_from_split_radiobtn = QRadioButton("from split ratio:")
        data_val_from_split_layout.addWidget(data_val_from_split_radiobtn)
        
        # QDoubleSpinBox to set validation split ratio
        self.split_ratio = QDoubleSpinBox()
        self.split_ratio.setRange(0.0, 1.0)
        self.split_ratio.setSingleStep(0.1)
        self.split_ratio.setDecimals(2)
        self.split_ratio.setValue(0.8)
        self.split_ratio.valueChanged.connect(self.sync_spinbox)
        data_val_from_split_layout.addWidget(self.split_ratio)

        data_val_from_split_layout.setStretchFactor(data_val_from_split_radiobtn, 0)
        data_val_from_split_layout.setStretchFactor(self.split_ratio, 1)
        ## END Layout from split ratio
        data_val_layout.addLayout(data_val_from_split_layout)
        
        # Layout validation data from image layer
        # Radio Button + ComboBox
        data_val_from_layer_layout = QHBoxLayout()
        data_val_from_layer_radiobtn = QRadioButton("from image layer:")
        data_val_from_layer_layout.addWidget(data_val_from_layer_radiobtn)
        
        # Drop-down to select layer as validation data
        self.layer_select.val = QComboBox()
        self._update_layer_select(self.layer_select.val)
        self.layer_select.val.activated.connect(lambda: self._update_layer_select(self.layer_select.val)) # update drop-down menu
        data_val_from_layer_layout.addWidget(self.layer_select.val)
        
        data_val_from_layer_layout.setStretchFactor(data_val_from_layer_radiobtn, 0)
        data_val_from_layer_layout.setStretchFactor(self.layer_select.val, 1)
        ## END Layout validation data from image layer
        data_val_layout.addLayout(data_val_from_layer_layout)

        # Connect radio button signals to toggle inputs
        self.radio_group.addButton(data_val_from_split_radiobtn, 1)
        self.radio_group.addButton(data_val_from_layer_radiobtn, 2)
        self.radio_group.buttonClicked.connect(self._toggle_radiobtn_inputs)
        self._toggle_radiobtn_inputs() # disable all inputs initially
        
        data_val_group.setLayout(data_val_layout)
        ## END Groupbox to setup validation data
        layout.addWidget(data_val_group)

        
        
        
        ## Groupbox to load model
        weights_group = QGroupBox("Model to train")        
        weights_layout = QVBoxLayout()

        # Buttongroup to setup validation data
        self.radio_group = QButtonGroup(self)

        model_new_radiobtn = QRadioButton("initialize new model")
        model_pre_radiobtn = QRadioButton("start from pretrained model")

        self.radio_group.addButton(model_new_radiobtn, 1)
        self.radio_group.addButton(model_pre_radiobtn, 2)
        
        weights_layout.addWidget(model_new_radiobtn)
        weights_layout.addWidget(model_pre_radiobtn)
        
        
        
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

        # Button to load pre-trained model
        self.load_model_button = QPushButton("Load pre-trained model") 
        self.load_model_button.clicked.connect(self._on_load_model_click)
        weights_layout.addWidget(self.load_model_button)
        
        weights_group.setLayout(weights_layout)
        ## END Groupbox to load model
        layout.addWidget(weights_group)
        

        
        # Connect radio button signals to toggle inputs
        self.radio_group.buttonClicked.connect(self._toggle_radiobtn_inputs)
        self._toggle_radiobtn_inputs() # disable all inputs initially
        

        
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
        
        # Widget to run training
        run_widget = QPushButton("Run training")
        run_widget.clicked.connect(self._on_run_click)
        self.run_btn = run_widget
        layout.addWidget(run_widget)
        
        layout.addStretch()
        self.setLayout(layout)
        
        for event in ["inserted", "removed", "moved"]:
            getattr(self.viewer.layers.events, event).connect(lambda e: self._update_layer_select(self.layer_select.train))
            getattr(self.viewer.layers.events, event).connect(lambda e: self._update_layer_select(self.layer_select.val))
        
        # Store a weights dir path
        self.sel_weights_dirpath = None
        self.load_weights_prefix = None

    def _toggle_radiobtn_inputs(self):
        selected_id = self.radio_group.checkedId()
        self.split_ratio.setEnabled(selected_id == 1)
        self.layer_select.val.setEnabled(selected_id == 2)
    
    def sync_spinbox(self, value):
        self.split_ratio.setValue(value)
        
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
        print(weight_filepaths)
        if weight_filepaths:
            weight_filenames = [os.path.basename(filepath) for filepath in weight_filepaths]
            weight_names = [filename.replace(".index", "") for filename in weight_filenames]
            self.weights_select.addItems(weight_names)
            self.log_widget.add_log('Found model weights!')
        else:
            self.log_widget.add_log(f'No model weights found!\nExpected contents: ckpt-*.index, ckpt-*.data.\nCheck weights directory path...')
    
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

    def _update_layer_select(self, layer_select):        
        current_layer = layer_select.currentText()
        layer_select.clear()

        layer_names = []
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.Image):
                layer_select.addItem(layer.name)
                layer_names.append(layer.name)
        
        if current_layer in layer_names:
            layer_select.setCurrentText(current_layer)
        elif layer_names:
            layer_select.setCurrentIndex(0)
        return layer_select
    
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