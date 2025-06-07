import os
import glob

from ._prediction_widget import PredictionWidget
from ._training_widget import TrainingWidget
from ._log_widget import LogWidget
from ._data_transform_widget import DataTransformWidget 

from qtpy.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel,
    QPushButton, QComboBox,
    QTabWidget, QWidget,
)

from qtpy import QtCore

import napari

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import napari

class DeBCRPlugin(QWidget):
    
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        
        self.viewer = viewer
        self.title = 'DeBCR: deblur microscopy images'
        self.main_tab = None
        self.log_widget = None
        
        self._init_layout()
        
    def _init_layout(self):

        layout = QVBoxLayout()
        
        # Title widget
        title_label = QLabel(self.title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Log widget
        self.log_widget = LogWidget()
        
        # Tab widget for subwidgets 
        self.main_tab = QTabWidget()

        ## Tab 1 : Data transform widget
        widget = DataTransformWidget(self.viewer, self.log_widget)
        self.main_tab.addTab(widget, 'Transform data')
        
        ## Tab 2 : Training widget
        widget = TrainingWidget(self.viewer, self.log_widget)
        self.main_tab.addTab(widget, 'Train model')
        
        ## Tab 3 : Prediction widget
        widget = PredictionWidget(self.viewer, self.log_widget)
        self.main_tab.addTab(widget, 'Use model')
        
        self.main_tab.setCurrentIndex(0)
        # END Tab widget for subwidgets
        layout.addWidget(self.main_tab)
        
        # Log widget: add to layout
        layout.addWidget(self.log_widget)
        
        self.setLayout(layout)