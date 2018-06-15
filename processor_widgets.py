import os
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel, QHBoxLayout, QListWidgetItem, QLineEdit
from PySide2.QtGui import QColor
from PySide2.QtCore import Qt
from qt_parameters import ParameterInteger, ParameterColor, ParameterCombobox
from qt_threads import CreatePdfThread, CreatePdfPagesThread


class ImageListItem(QListWidgetItem):
    def __init__(self, *args):
        super(ImageListItem, self).__init__(args[0])
        self.id = args[1]

    def get_data(self):
        return self.id


class OptionsFromSourceWidget(QWidget):
    def __init__(self, label_width=64, status_bar=None):
        super(OptionsFromSourceWidget, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.status_bar = status_bar
        self.pixels = 10
        self.margin = 0
        self.background = QColor(255, 255, 255)
        pixel_param = ParameterInteger(self, value=self.pixels, max_visible=64, min_value=1, name="pixels", label_text="Pix per Unit", label_width=label_width, change_callback=self.chenge_value_callback)
        margin_param = ParameterInteger(self, value=self.margin, max_visible=64, min_value=0, name="margin", label_text="Margin", label_width=label_width, change_callback=self.chenge_value_callback)
        back_color = ParameterColor(self, value=self.background, name="background", label_text="Background", label_width=label_width, change_callback=self.chenge_value_callback)
        layout.addWidget(pixel_param)
        layout.addWidget(margin_param)
        layout.addWidget(back_color)
        self.setLayout(layout)

    def chenge_value_callback(self, param_name="", param_value=None):
        if param_name == "pixels":
            self.pixels = param_value
            if self.status_bar is not None:
                self.status_bar.showMessage("Set pixels per unit to " + str(self.pixels))
        elif param_name == "margin":
            self.margin = param_value
            if self.status_bar is not None:
                self.status_bar.showMessage("Set margin to " + str(self.margin) + " pixels")
        elif param_name == "background":
            self.background = param_value
            if self.status_bar is not None:
                self.status_bar.showMessage("Set background color to RGB(" + ", ".join([str(self.background.red()), str(self.background.green()), str(self.background.blue())]) + ")")

    def get_pixel_value(self):
        return self.pixels

    def get_margin_value(self):
        return self.margin

    def get_background_value(self):
        return (self.background.red(), self.background.green(), self.background.blue())


class OptionsAWidget(QWidget):
    def __init__(self, label_width=64, status_bar=None):
        super(OptionsAWidget, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.status_bar = status_bar
        self.margin = 50
        self.align = 0
        self.background = QColor(255, 255, 255)
        margin_param = ParameterInteger(self, value=self.margin, max_visible=128, min_value=0, name="margin", label_text="Margin", label_width=label_width,  change_callback=self.chenge_value_callback)
        align_param = ParameterCombobox(self, value=0, items=["Center", "Center-Top", "Center-Bottom", "Left-Top", "Left-Center", "Left-Bottom", "Right-Top", "Right-Center", "Right-Bottom"], name="align", label_text="Align", label_width=label_width, change_callback=self.chenge_value_callback)
        back_color = ParameterColor(self, value=self.background, name="background", label_text="Background", label_width=label_width, change_callback=self.chenge_value_callback)
        layout.addWidget(margin_param)
        layout.addWidget(align_param)
        layout.addWidget(back_color)
        self.setLayout(layout)

    def chenge_value_callback(self, param_name="", param_value=None):
        if param_name == "margin":
            self.margin = param_value
            if self.status_bar is not None:
                self.status_bar.showMessage("Set margin to " + str(self.margin) + " units")
        elif param_name == "align":
            self.align = param_value[0]
            if self.status_bar is not None:
                self.status_bar.showMessage("Set align to " + str(param_value[1][self.align]))
        elif param_name == "background":
            self.background = param_value
            if self.status_bar is not None:
                self.status_bar.showMessage("Set background color to RGB(" + ", ".join([str(self.background.red()), str(self.background.green()), str(self.background.blue())]) + ")")

    def get_margin_value(self):
        return self.margin

    def get_align_value(self):
        return self.align

    def get_background_value(self):
        return (self.background.red(), self.background.green(), self.background.blue())


class SelectWidget(QGroupBox):
    def __init__(self, click_move_up, click_move_down, click_invert, click_delete):
        super(SelectWidget, self).__init__()
        BUTTON_SIZE = 26
        self.setTitle("Selection")
        self.setMaximumHeight(250)
        self.setMinimumWidth(150)
        select_zone_layout = QVBoxLayout()
        select_zone_layout.setAlignment(Qt.AlignTop)

        select_move_up_button = QPushButton("\u2191")
        select_move_up_button.clicked.connect(click_move_up)
        select_move_up_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        select_move_up_label = QLabel("Move Up")
        select_move_up = QHBoxLayout()
        select_move_up.addWidget(select_move_up_button)
        select_move_up.addWidget(select_move_up_label)
        select_zone_layout.addLayout(select_move_up)

        select_move_down_button = QPushButton("\u2193")
        select_move_down_button.clicked.connect(click_move_down)
        select_move_down_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        select_move_down_label = QLabel("Move Down")
        select_move_down = QHBoxLayout()
        select_move_down.addWidget(select_move_down_button)
        select_move_down.addWidget(select_move_down_label)
        select_zone_layout.addLayout(select_move_down)

        select_invert_button = QPushButton("||")
        select_invert_button.clicked.connect(click_invert)
        select_invert_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        select_invert_label = QLabel("Invert")
        select_invert = QHBoxLayout()
        select_invert.addWidget(select_invert_button)
        select_invert.addWidget(select_invert_label)
        select_zone_layout.addLayout(select_invert)

        select_delete_button = QPushButton("\u2A09")
        select_delete_button.clicked.connect(click_delete)
        select_delete_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        select_delete_label = QLabel("Delete")
        select_delete = QHBoxLayout()
        select_delete.addWidget(select_delete_button)
        select_delete.addWidget(select_delete_label)
        select_zone_layout.addLayout(select_delete)

        self.setLayout(select_zone_layout)


class CreatePdfWidget(QWidget):
    def __init__(self, get_data, status_link):
        super(CreatePdfWidget, self).__init__()
        self.get_data_method = get_data
        self.status_bar = status_link
        layout = QHBoxLayout()
        path_label = QLabel("Path: ")
        path_to_save = os.path.split(os.path.realpath(__file__))[0] + "\\selection.pdf"
        self.path_line_edit = QLineEdit(path_to_save)
        save_button = QPushButton("Create Pdf")
        save_button.setMinimumHeight(28)
        save_button.clicked.connect(self.click_create_pdf)
        layout.addWidget(path_label)
        layout.addWidget(self.path_line_edit)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def click_create_pdf(self):
        data = self.get_data_method()
        if data is not None:
            path_to_save = self.path_line_edit.text()
            if path_to_save[-4:] != ".pdf" and path_to_save[-4:] != ".PDF":
                path_to_save += ".pdf"
            # create directory if we should
            dir_path = os.path.split(path_to_save)[0]
            if os.path.exists(dir_path) is False:
                os.makedirs(dir_path)
            if data[0] == 0:  # this is for creatin pdf from images
                files = data[1]
                image_params = data[2]  # {'mode': 0, 'pixels': 10, 'margin': 0} or {'mode': 1, 'align': 0, 'margin': 0}
                self._create_pdf_from_images(path_to_save, files, image_params)
            elif data[0] == 1:  # create pdf from pages of the other pdfs
                pages_dict = data[1]
                self._create_pdf_from_pages(path_to_save, pages_dict)
            else:
                print("Unsupported mode " + str(data[0]))

    def update_step_callback(self, callback_data):  # data in the form (current step, total steps)
        self.status_bar.showMessage("Create " + str(callback_data[0]) + " page from " + str(callback_data[1]) + " total pages")

    def finish_callback(self):
        self.status_bar.showMessage("Done!")

    def message_callback(self, message):
        self.status_bar.showMessage(message)

    def _create_pdf_from_images(self, path_to_save, path_array, img_params):
        self.create_thread = CreatePdfThread(path_to_save, (path_array, img_params))
        self.create_thread.step_signal.connect(self.update_step_callback)
        self.create_thread.finished.connect(self.finish_callback)
        self.create_thread.message_signal.connect(self.message_callback)
        self.create_thread.start()

    def _create_pdf_from_pages(self, path_to_save, pages_dict):
        self.create_thread = CreatePdfPagesThread(path_to_save, pages_dict)
        self.create_thread.step_signal.connect(self.update_step_callback)
        self.create_thread.finished.connect(self.finish_callback)
        self.create_thread.message_signal.connect(self.message_callback)
        self.create_thread.start()
