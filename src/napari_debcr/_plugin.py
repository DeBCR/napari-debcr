import os
import glob

from ._inference_widget import DeBCRInferenceWidget
from ._training_widget import DeBCRTrainingWidget
from ._log_widget import DeBCRLogWidget

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
        self.log_widget = DeBCRLogWidget()
        
        # Tab widget for subwidgets 
        self.main_tab = QTabWidget()

        ## Tab 1 : Inference widget
        widget = DeBCRTrainingWidget(self.viewer, self.log_widget)
        self.main_tab.addTab(widget, 'Train')
        
        ## Tab 2 : Inference widget
        widget = DeBCRInferenceWidget(self.viewer, self.log_widget)
        self.main_tab.addTab(widget, 'Predict')
        
        self.main_tab.setCurrentIndex(0)
        # END Tab widget for subwidgets
        layout.addWidget(self.main_tab)
        
        # Log widget: add to layout
        layout.addWidget(self.log_widget)
        
        self.setLayout(layout)