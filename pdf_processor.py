import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import QEvent

from tab_image_to_pdf import ImageToPdfWidget
from tab_synth_pdf import SynthPdfWidget
from processor_widgets import CreatePdfWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.set_style()
        self.setWindowTitle("PDF Processor")
        self.installEventFilter(self)
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.status_bar = self.statusBar()
        self.tab_widget = QTabWidget()
        self.tab_imageToPdf = ImageToPdfWidget(self.status_bar)
        self.tab_extractPdf = SynthPdfWidget(self.status_bar)
        self.tab_widget.addTab(self.tab_imageToPdf, "Image To Pdf")
        self.tab_widget.addTab(self.tab_extractPdf, "Synth Pdf")

        layout.addWidget(self.tab_widget)
        create_widget = CreatePdfWidget(self.get_data, self.status_bar)
        layout.addWidget(create_widget)

        self.setCentralWidget(central_widget)
        self.resize(1280, 720)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.status_bar.showMessage("")
        return QMainWindow.eventFilter(self, source, event)

    def set_style(self):
        appQt.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(235, 101, 54))
        palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        appQt.setPalette(palette)

    def get_data(self):
        tab_index = self.tab_widget.currentIndex()
        if tab_index == 0:  # this is img->pdf
            return (0, self.tab_imageToPdf.get_images_to_save(), self.tab_imageToPdf.get_image_parameters())
        elif tab_index == 1:  # this is synth pdf
            return (1, self.tab_extractPdf.extern_get_files_and_pages())


if __name__ == '__main__':
    appQt = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    appQt.exec_()
