from qtpy.QtWidgets import (
    QVBoxLayout,
    QTextEdit,
    QWidget,
)

class DeBCRLogWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def add_log(self, message: str):
        self.log_box.append(f'\n{message}')

    #def clear_log(self):
    #    self.log_box.clear()
    