from qtpy.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit,
    QPushButton, QSpinBox, QDoubleSpinBox, QCheckBox,
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
    result_signal = Signal(object, str)  # Signal to pass transform results (image data, image name)
    param_signal = Signal(tuple) # Signal to update parameter patches_num
    
    def __init__(self, widget, action):
        super().__init__()
        self.widget = widget
        self.action = action
    
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

        if self.action == 'crop':
            args_list = ['overlap', 'patch_size']
        elif self.action == 'stitch':
            args_list = ['overlap', 'patch_num', 'use_cosine']
        elif self.action == 'normalize':
            args_list = ['pmin', 'pmax']
        else:
            args_list = []
        
        run_args = {run_arg: getattr(self.widget, run_arg) for run_arg in args_list}

        run_action = getattr(debcr.data, self.action)
        output_data = run_action(input_data, **run_args)
        
        output_name = self.widget.layer_out.text()
        self.result_signal.emit(output_data, output_name)

        if self.action == 'crop':
            _,patch_num = debcr.data.crop(input_data, **run_args, dry_run=True)
            self.param_signal.emit(patch_num)
        
        self.log_signal.emit(f'New data shape: {output_data.shape}')
        self.finished_signal.emit()  # Notify UI when done
    
class DataTransformWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer
        self.log_widget = log_widget

        self.layer_select = None
        self.layer_out = None
        self.patch_size = 128 # default
        self.patch_num = (1,1)
        self.overlap = (0.5, 0.5) # default
        self.use_cosine = True # default
        self.pmin = 0.1 # default
        self.pmax = 99.9 # default
        
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
        # Layout: clip by percentiles
        perc_layout = QHBoxLayout()

        perc_layout.addWidget(QLabel("normalize by percentile (pmin,pmax):"))
        self.pmin_spin = QDoubleSpinBox()
        self.pmin_spin.setDecimals(2)
        self.pmin_spin.setRange(0, 100)
        self.pmin_spin.setSingleStep(0.1)
        self.pmin_spin.setValue(self.pmin) # default
        self.pmin_spin.valueChanged.connect(self._update_pmin)
        perc_layout.addWidget(self.pmin_spin)
        
        self.pmax_spin = QDoubleSpinBox()
        self.pmax_spin.setDecimals(2)
        self.pmax_spin.setRange(0, 100)
        self.pmax_spin.setSingleStep(0.1)
        self.pmax_spin.setValue(self.pmax) # default
        self.pmax_spin.valueChanged.connect(self._update_pmax)
        perc_layout.addWidget(self.pmax_spin)
        # END Layout: clip by percentiles range
        #########
        params_layout.addLayout(perc_layout)
        
        #########
        # Layout: patch size
        patch_size_layout = QHBoxLayout()
        patch_size_layout.addWidget(QLabel("patch size (XY):"))
        self.patch_size_spin = QSpinBox()
        self.patch_size_spin.setRange(32, 256)
        self.patch_size_spin.setSingleStep(16)
        self.patch_size_spin.setValue(self.patch_size) # default
        self.patch_size_spin.valueChanged.connect(self._update_patch_size)
        patch_size_layout.addWidget(self.patch_size_spin)
        # END Layout: patch size
        #########
        params_layout.addLayout(patch_size_layout)

        #########
        # Layout: patch overlap
        overlap_layout = QHBoxLayout()
        overlap_layout.addWidget(QLabel("patch overlap (X,Y):"))
        
        self.overlap_x_spin = QDoubleSpinBox()
        self.overlap_x_spin.setDecimals(2)
        self.overlap_x_spin.setRange(0, 1)
        self.overlap_x_spin.setSingleStep(0.25)
        self.overlap_x_spin.setValue(0.50) # default
        self.overlap_x_spin.valueChanged.connect(self._update_overlap_x)
        overlap_layout.addWidget(self.overlap_x_spin)

        self.overlap_y_spin = QDoubleSpinBox()
        self.overlap_y_spin.setDecimals(2)
        self.overlap_y_spin.setRange(0, 1)
        self.overlap_y_spin.setSingleStep(0.25)
        self.overlap_y_spin.setValue(0.50) # default
        self.overlap_y_spin.valueChanged.connect(self._update_overlap_y)
        overlap_layout.addWidget(self.overlap_y_spin)
        # END Layout: patch overlap
        #########
        params_layout.addLayout(overlap_layout)

        #########
        # Layout: patch num
        patch_num_layout = QHBoxLayout()
        patch_num_layout.addWidget(QLabel("patch count (X,Y):"))
        
        self.patch_nx_spin = QSpinBox()
        self.patch_nx_spin.setRange(1, 64)
        self.patch_nx_spin.setSingleStep(4)
        self.patch_nx_spin.setValue(1) # default
        self.patch_nx_spin.valueChanged.connect(self._update_patch_nx)
        patch_num_layout.addWidget(self.patch_nx_spin)
        
        self.patch_ny_spin = QSpinBox()
        self.patch_ny_spin.setRange(1, 64)
        self.patch_ny_spin.setSingleStep(4)
        self.patch_ny_spin.setValue(1) # default
        self.patch_ny_spin.valueChanged.connect(self._update_patch_ny)
        patch_num_layout.addWidget(self.patch_ny_spin)
        # END Layout: patch num
        #########
        params_layout.addLayout(patch_num_layout)

        # Check-box: use cosine blending
        self.use_cosine_ckbox = QCheckBox("use cosine blending for stitching")
        self.use_cosine_ckbox.setChecked(self.use_cosine)
        self.use_cosine_ckbox.stateChanged.connect(self._update_use_cosine)
        params_layout.addWidget(self.use_cosine_ckbox)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        #########
        # Layout: normalize / crop / stitich
        run_btns_layout = QHBoxLayout()
        self.run_btns = {}

        ## Button: normalize data
        self.run_btns['normalize'] = QPushButton("Normalize")
        self.run_btns['normalize'].clicked.connect(lambda: self._on_run_click('normalize'))
        run_btns_layout.addWidget(self.run_btns['normalize'])
        
        ## Button: crop patches
        self.run_btns['crop'] = QPushButton("Crop")
        self.run_btns['crop'].clicked.connect(lambda: self._on_run_click('crop'))
        run_btns_layout.addWidget(self.run_btns['crop'])

        ## Button: stitch patches
        self.run_btns['stitch'] = QPushButton("Stitch")
        self.run_btns['stitch'].clicked.connect(lambda: self._on_run_click('stitch'))
        run_btns_layout.addWidget(self.run_btns['stitch'])
        # END Layout: crop / stitich
        #########
        layout.addLayout(run_btns_layout)
        
        layout.addStretch()
        self.setLayout(layout)

    def _update_pmin(self, value):
        self.pmin = value

    def _update_pmax(self, value):
        self.pmax = value
    
    def _update_patch_size(self, value):
        self.patch_size = value

    def _update_patch_nx(self, value):
        self.patch_num = (value, self.patch_num[1])

    def _update_patch_ny(self, value):
        self.patch_num = (self.patch_num[0], value)
    
    def _update_overlap_x(self, value):
        self.overlap = (value, self.overlap[1])
    
    def _update_overlap_y(self, value):
        self.overlap = (self.overlap[0], value)
    
    def _on_run_click(self, action):
        self._toggle_run_btn(False, action)
        # Run data transform in a background thread
        self.thread = DataTransformThread(self, action)
        self.thread.log_signal.connect(self.log_widget.add_log)
        self.thread.result_signal.connect(self._add_result_layer)
        self.thread.param_signal.connect(self._update_patch_num)
        self.thread.finished_signal.connect(lambda: self._toggle_run_btn(True, action))
        self.thread.start()

    def _update_use_cosine(self):
        self.use_cosine = self.use_cosine_ckbox.isChecked()
    
    def _update_patch_num(self, patch_num):
        self.patch_num = patch_num
        self._update_patch_num_spin()
        
    def _update_patch_num_spin(self):
        self.patch_nx_spin.setValue(self.patch_num[0])
        self.patch_ny_spin.setValue(self.patch_num[1])
        
    def _add_result_layer(self, image_data, image_name):
        self.viewer.add_image(image_data, name=image_name)
    
    def _toggle_run_btn(self, enabled, action):
        if enabled:
            self.run_btns[action].setText(action.title())
            self.run_btns[action].setEnabled(True)
        else:
            self.run_btns[action].setText("Running: " + action + "...")
            self.run_btns[action].setEnabled(False)
            QApplication.processEvents()