from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import Qt, QPoint
from ksb_pyside_kit.core.commons import QObject, Signal
from ksb_pyside_kit.core.base_widget import BaseWidget
from ksb_pyside_kit.core.themes.themes import ThemeManager
from ksb_pyside_kit.widgets.text import Text

class ProgressBar(BaseWidget):
    """
    Custom progress bar widget
    """
    def __init__(
        self,
        key: str = "",
        label: str = "Progression...",
        minimum: int = 0,
        maximum: int = 100,
        width: int = 300,
        height: int = 80,
        theme = ThemeManager.ProgressBarThemes.DEFAULT,
        parent=None,
        **kwargs
    ):
        self.key = key
        self._label_text = label
        self._minimum = minimum
        self._maximum = maximum
        super().__init__(key=key, theme=theme, parent=parent, **kwargs)
        self._width = width
        self._height = height
        self.setObjectName("progress-bar")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._dragging = False
        self._drag_position = QPoint()
        self.setFixedSize(self._width, self._height)
        
    def _setup_ui(self):
        self.label = Text(
            value=self._label_text,
            theme=ThemeManager.TextThemes.LABEL,
            align="center"
        )
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(self._minimum)
        self.progress_bar.setMaximum(self._maximum)
        self.progress_bar.setValue(self._minimum)
        self.progress_bar.setTextVisible(True)
        
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.setSpacing(10)
        self.main_layout.addStretch(1)
        
    def set_label(self, text: str):
        self.label.text = text

    def set_range(self, minimum: int, maximum: int):
        self.progress_bar.setMinimum(minimum)
        self.progress_bar.setMaximum(maximum)

    def set_value(self, value: int):
        self.progress_bar.setValue(value)

    def set_text_visible(self, visible: bool):
        self.progress_bar.setTextVisible(visible)

    def set_format(self, format_str: str):
        """
        Exemple : set_format("%p% terminé")
        """
        self.progress_bar.setFormat(format_str)

    def reset(self):
        self.progress_bar.reset()

    def apply_theme(self, theme):
        """
        Applique le thème au widget et à la barre de progression.
        """
        super().apply_theme(theme)
        if theme and hasattr(theme, 'get_stylesheet'):
            self.progress_bar.setStyleSheet(theme.get_stylesheet())

    def mousePressEvent(self, event):
        """Gérer le clic de souris pour commencer le déplacement"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Gérer le déplacement de la fenêtre"""
        if event.buttons() & Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Gérer le relâchement du clic pour arrêter le déplacement"""
        if event.button() == Qt.LeftButton:
            self._dragging = False
            event.accept()
            
class ProgressWorker(QObject):
    progress_changed = Signal(int, int)
    label_changed = Signal(str)
    finished = Signal(object) 
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        """
        func: function to run in the worker thread
        args: arguments to pass to func
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            result = self.func(
                *self.args,
                progress_callback=self._progress_callback,
                label_callback=self._label_callback,
                is_running=lambda: self._is_running
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _progress_callback(self, value, total):
        self.progress_changed.emit(value, total)

    def _label_callback(self, text):
        self.label_changed.emit(text)
        
# # --- Exemple d'utilisation réutilisable ---
# if __name__ == "__main__":
#     import sys
#     import time
#     from PySide6.QtCore import Qt, QObject, QThread, Signal
#     from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

#     def long_task(progress_callback, label_callback, is_running, total=100):
#         for i in range(1, total + 1):
#             if not is_running():
#                 break
#             time.sleep(0.03)
#             progress_callback(i, total)
#             label_callback(f"Traitement : {i}/{total}")
#         label_callback("Terminé !")
#         return "Résultat final"

#     app = QApplication(sys.argv)
#     window = QWidget()
#     layout = QVBoxLayout(window)

#     progress = ProgressBar(label="Traitement en cours...", maximum=100, theme=ThemeManager.ProgressBarThemes.SUCCESS)
#     layout.addWidget(progress)

#     start_btn = QPushButton("Démarrer le traitement")
#     layout.addWidget(start_btn)

#     window.worker = None
#     window.thread = None

#     def start_process():
#         progress.set_value(0)
#         progress.set_label("Traitement en cours...")
#         start_btn.setEnabled(False)

#         window.worker = ProgressWorker(long_task, total=100)
#         window.thread = QThread()
#         window.worker.moveToThread(window.thread)

#         window.worker.progress_changed.connect(lambda val, total: progress.set_value(val))
#         window.worker.label_changed.connect(progress.set_label)
#         window.worker.finished.connect(lambda result: progress.set_label(f"Fini ({result})"))
#         window.worker.finished.connect(window.thread.quit)
#         window.worker.finished.connect(lambda _: start_btn.setEnabled(True))
#         window.worker.error.connect(lambda err: progress.set_label(f"Erreur : {err}"))
#         window.thread.started.connect(window.worker.run)
#         window.thread.start()

#     start_btn.clicked.connect(start_process)

#     window.setWindowTitle("Démo ProgressBar Générique")
#     window.resize(400, 150)
#     window.show()
#     sys.exit(app.exec())
