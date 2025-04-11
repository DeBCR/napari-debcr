from qtpy.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout, QVBoxLayout,
    QLabel,
    QPushButton, QSpinBox,
    QWidget,
)
from qtpy.QtCore import QThread, Signal, Qt

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

from ._input_data_widget import InputDataGroupBox
from ._load_weights_widget import LoadWeightsGroupBox
from ._model_configs_widget import ModelConfigsGroupBox

import debcr

class TrainingThread(QThread):
    finished_signal = Signal()  # Signal to notify when finished
    log_signal = Signal(str) # Signal for log messages
    result_signal = Signal(object)  # Signal to pass prediction results (image data, name)
    
    def __init__(self, widget, config, model):
        super().__init__()
        self.widget = widget
        self.config = config
        self.model = model
    
    def get_layer_by_name(self, input_name):
        
        input_data = None
        
        for layer in self.widget.viewer.layers:
            if isinstance(layer, napari.layers.Image) and (layer.name == input_name) and (layer.data is not None):
                input_data = layer.data
                break
        
        return input_data

    def abort_training(self, message):
        self.log_signal.emit(f'{message}\nTraining is aborted.')
        self.finished_signal.emit()
        
    def run(self):
        
        data = {"train": {}, "val": {}}
        for dataset in ["train", "val"]:
            for subset in ["low", "gt"]:
                key = f"{dataset}.{subset}"
                input_name = self.widget.data_widgets[key].layer_select.currentText()
                input_data = self.get_layer_by_name(input_name)
                
                if input_data is None:
                    self.abort_training(message = f'Image stack not found: \'{input_name}\'')
                
                data[dataset][subset] = input_data

        labels = {
            "train": "training",
            "val": "validation",
            "low": "input",
            "gt": "target"
        }
        expected_shape = data["train"]["low"].shape[-2:]
        equal_subset_shapes = True
        for dataset in ["train", "val"]:
            for subset in ["low", "gt"]:
                input_data = data[dataset][subset]
                input_shape = input_data.shape[-2:]
                input_label = labels[dataset] + " " + labels[subset]
                
                if input_shape[0] != input_shape[1]:
                    self.abort_training(f'\'{input_label}\' images are not non-square: {input_shape}')
                elif input_shape != expected_shape:
                    self.abort_training(f'\'{input_label}\' shape {input_shape} and training input shape {expected_shape} are different!')
        
        self.log_signal.emit('Starting model training...')
        
        model_trained = debcr.model.train(data["train"], data["val"], self.config, self.model)
        
        self.result_signal.emit(model_trained)
        self.log_signal.emit('Training is finished!')
        
        self.finished_signal.emit()  # Notify UI when done
        
class TrainingWidget(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer", log_widget):
        super().__init__()
        
        self.viewer = viewer
        self.log_widget = log_widget
        self.data_widgets = {}
        
        self.train_config = None
        self.debcr = None
        
        self._init_layout()
        
    def _init_layout(self):
        
        layout = QVBoxLayout()
        
        # Widget: train input data
        self.data_widgets["train.low"] = InputDataGroupBox(self.viewer, 'Training input')
        layout.addWidget(self.data_widgets["train.low"])

        # Widget: train GT data
        self.data_widgets["train.gt"] = InputDataGroupBox(self.viewer, 'Training target')
        layout.addWidget(self.data_widgets["train.gt"])

        # Widget: trained model
        weigths_widget = LoadWeightsGroupBox(self.viewer, "Model to train", self.log_widget, add_init_ckbox=True)
        layout.addWidget(weigths_widget)
        
        # Widget: validation input data
        self.data_widgets["val.low"] = InputDataGroupBox(self.viewer, 'Validation input')
        layout.addWidget(self.data_widgets["val.low"])

        # Widget: validation GT data
        self.data_widgets["val.gt"] = InputDataGroupBox(self.viewer, 'Validation target')
        layout.addWidget(self.data_widgets["val.gt"])
        
        # Widget: training parameters
        params_group = ModelConfigsGroupBox(self.viewer, 'Training configurations', self.log_widget)
        layout.addWidget(params_group)
        
        # Widget: run training
        run_widget = QPushButton("Run training")
        run_widget.clicked.connect(lambda: self._on_run_click(weigths_widget.debcr, params_group.config))
        self.run_btn = run_widget
        layout.addWidget(run_widget)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Store a weights dir path
        self.sel_weights_dirpath = None
        self.load_weights_prefix = None
        
    def _on_run_click(self, model, config):
        
        self.debcr = model
        if self.debcr is None:
            self.log_widget.add_log(f'No model initialized or loaded yet!')
            return
        
        self._toggle_run_btn(False)

        self.train_config = config
        self.log_widget.add_log(f'Params: {config}')
        
        # Run trainig in a background thread
        self.thread = TrainingThread(self, self.train_config, self.debcr)
        self.thread.log_signal.connect(self.log_widget.add_log)
        self.thread.result_signal.connect(self._update_model_object)
        self.thread.finished_signal.connect(lambda: self._toggle_run_btn(True))
        self.thread.start()

    def _update_model_object(self, trained_model):
        self.debcr = trained_model
    
    def _toggle_run_btn(self, enabled):
        if enabled:
            self.run_btn.setText("Run training")
            self.run_btn.setEnabled(True)
        else:
            self.run_btn.setText("Running training...")
            self.run_btn.setEnabled(False)
            QApplication.processEvents()