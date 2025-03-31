from qtpy.QtWidgets import (
    QVBoxLayout,
    QLabel, QTextEdit,
    QPushButton,
    QWidget,
)

class DeBCRLogWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        # TextEdit: log window widget
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # Button: clear log
        clear_widget = QPushButton("Clear log")
        clear_widget.clicked.connect(self._on_clear_click)
        self.clear_btn = clear_widget
        layout.addWidget(clear_widget)
        
        self.setLayout(layout)

    def add_log(self, message: str):
        self.log_box.append(f'\n{message}')

    def _on_clear_click(self):
        self.log_box.clear()
    