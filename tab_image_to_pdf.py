import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QListWidget, QAbstractItemView, QVBoxLayout, QGroupBox, QComboBox, QLabel, QPushButton, QSlider, QFileDialog
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QImage, QPixmap
from PIL import Image
from processor_widgets import OptionsFromSourceWidget, OptionsAWidget, SelectWidget, ImageListItem


class ImageToPdfWidget(QWidget):
    def __init__(self, status_link):
        super(ImageToPdfWidget, self).__init__()
        LABEL_WIDTH = 80
        self.last_selected_items = []
        self.options_mode = 0
        self.update_status_combobox = False
        layout = QHBoxLayout()
        self.status_bar = status_link
        self.list_view = QListWidget()
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.itemClicked.connect(self.click_item_signal)
        self.list_view.itemEntered.connect(self.click_item_signal)
        self.list_view.itemSelectionChanged.connect(self.change_selection_signal)

        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignTop)

        select_zone = SelectWidget(self.click_move_up, self.click_move_down, self.click_invert, self.click_delete)

        # options zone -------------------------------------
        options_zone = QGroupBox("Options")
        self.options_zone_layout = QVBoxLayout()

        self.options_mode_combobox = QComboBox()
        self._add_items_to_mode_combobox(self.options_mode_combobox)
        options_mode_label = QLabel("Mode")
        options_mode_label.setMaximumWidth(LABEL_WIDTH)
        options_mode_layout = QHBoxLayout()
        options_mode_layout.addWidget(options_mode_label)
        options_mode_layout.addWidget(self.options_mode_combobox)
        self.options_zone_layout.addLayout(options_mode_layout)
        self.option_source_widget = OptionsFromSourceWidget(label_width=LABEL_WIDTH, status_bar=self.status_bar)
        self.options_a_widget = OptionsAWidget(label_width=LABEL_WIDTH, status_bar=self.status_bar)
        self.options_mode_combobox.currentIndexChanged.connect(self.change_options_mode_signal)
        self.change_options_mode_signal(self.options_mode)

        options_zone.setLayout(self.options_zone_layout)

        # Add files button and final structures ---------------------------
        add_file_button = QPushButton("Add Files")
        add_file_button.clicked.connect(self.click_add_files)
        controls_layout.addWidget(select_zone)
        controls_layout.addWidget(options_zone)
        controls_layout.addWidget(add_file_button)

        # image preview ---------------------------------------------------
        image_prev_layout = QVBoxLayout()
        image_prev_layout.setContentsMargins(0, 0, 4, 0)
        self.IMG_PREVIEW_WIDTH = 256
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.select_text = "Click item to preview"
        self.last_created_pix_path = ""
        self.img_label.setText(self.select_text)
        image_prev_layout.addWidget(self.img_label)
        # slider for the preview scale
        self.img_scale_slider = QSlider()
        self.img_scale_slider.setMinimum(6)
        self.img_scale_slider.setMaximum(2048)
        self.img_scale_slider.setValue(self.IMG_PREVIEW_WIDTH)
        self.img_scale_slider.setOrientation(Qt.Horizontal)
        self.img_scale_slider.valueChanged.connect(self.change_scale_slider_signal)
        image_prev_layout.addWidget(self.img_scale_slider)
        self._update_preview()

        layout.addLayout(image_prev_layout)
        layout.addWidget(self.list_view)
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        self.update_status_combobox = True

    def _pillow_to_pixmap(self, img):
        if img.mode == "RGB":
            r, g, b = img.split()
            img = Image.merge("RGB", (b, g, r))
        elif img.mode == "RGBA":
            r, g, b, a = img.split()
            img = Image.merge("RGBA", (b, g, r, a))
        elif img.mode == "L":
            img = img.convert("RGBA")
        img2 = img.convert("RGBA")
        data = img2.tobytes("raw", "RGBA")
        qim = QImage(data, img.size[0], img.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def _update_preview(self):
        self.img_label.setMinimumWidth(self.IMG_PREVIEW_WIDTH)
        self.img_label.setMaximumWidth(max(self.IMG_PREVIEW_WIDTH, self.img_scale_slider.width()))
        if len(self.last_created_pix_path) > 0:
            img = Image.open(self.last_created_pix_path)
            img_pix = self._pillow_to_pixmap(img)
            img_pix = img_pix.scaled(QSize(self.IMG_PREVIEW_WIDTH, self.IMG_PREVIEW_WIDTH), Qt.KeepAspectRatio)
            self.img_label.setPixmap(img_pix)

    def _set_preview(self, img_path):
        if img_path is None:
            self.last_created_pix_path = ""
            self.img_label.setText(self.select_text)
        else:
            if img_path != self.last_created_pix_path:
                self.last_created_pix_path = img_path
                self._update_preview()

    def _add_items_to_mode_combobox(self, combobox):
        combobox.addItem("From Source")
        combobox.addItem("A4")
        # combobox.addItem("A5")
        # combobox.addItem("A6")
        # combobox.addItem("Letter")

    def _get_filtered_string(self, string):
        to_return_array = []
        for s in string:
            if s.isdigit():
                to_return_array.append(s)
        return "".join(to_return_array)

    def get_images_to_save(self):
        path_array = []
        for i in range(self.list_view.count()):
            path_array.append(self.list_view.item(i).get_data())
        return path_array

    def get_image_parameters(self):  # return as dictionary
        if self.options_mode == 0:
            return {"mode": 0,
                    "pixels": self.option_source_widget.get_pixel_value(),
                    "margin": self.option_source_widget.get_margin_value(),
                    "background": self.option_source_widget.get_background_value()}
        else:
            return {"mode": self.options_mode,
                    "align": self.options_a_widget.get_align_value(),
                    "margin": self.options_a_widget.get_margin_value(),
                    "background": self.options_a_widget.get_background_value()}

    def add_items(self, array):
        added_names = []
        for a in array:
            new_name = os.path.basename(a)
            new_item = ImageListItem(new_name, a)
            added_names.append(new_name)
            self.list_view.addItem(new_item)
        self.status_bar.showMessage("Add items: " + ", ".join(added_names))

    def change_scale_slider_signal(self, value):
        self.IMG_PREVIEW_WIDTH = value
        self._update_preview()
        self.status_bar.showMessage("Set preview scale to " + str(value))

    def click_item_signal(self, item):
        pass
        # self._set_preview(item.get_data())
        # self.status_bar.showMessage("Select " + str(item.text()))

    def _get_first_new_index(self, current, last):
        for v in current:
            if v not in last:
                return v
        return current[0]

    def change_selection_signal(self):
        if len(self.list_view.selectedItems()) == 0:
            self._set_preview(None)  # nothing selected
        else:
            selected_indexes = [self.list_view.indexFromItem(sel).row() for sel in self.list_view.selectedItems()]
            item = self.list_view.item(self._get_first_new_index(selected_indexes, self.last_selected_items))
            self._set_preview(item.get_data())
            self.status_bar.showMessage("Select " + str(item.text()))
            self.last_selected_items = selected_indexes

    def change_options_mode_signal(self, index):
        self.options_mode = index
        if self.options_mode == 0:
            self.options_zone_layout.removeWidget(self.options_a_widget)
            self.options_a_widget.setParent(None)
            self.options_zone_layout.addWidget(self.option_source_widget)
        else:
            self.options_zone_layout.removeWidget(self.option_source_widget)
            self.option_source_widget.setParent(None)
            self.options_zone_layout.addWidget(self.options_a_widget)
        if self.update_status_combobox:
            self.status_bar.showMessage("Set combine mode to \"" + self.options_mode_combobox.itemText(index) + "\"")

    def resizeEvent(self, size):
        # self._update_preview()
        pass

    def click_move_up(self):
        selected = self.list_view.selectedItems()
        selected_indexes = [self.list_view.indexFromItem(sel).row() for sel in selected]
        selected_indexes.sort()
        if len(selected_indexes) > 0 and selected_indexes[0] > 0:
            for index in selected_indexes:
                prev_item = self.list_view.takeItem(index - 1)
                self.list_view.insertItem(index, prev_item)
            self.status_bar.showMessage("Move " + str(len(selected_indexes)) + " items")
        else:
            self.status_bar.showMessage("Nothing to move")

    def click_move_down(self):
        selected = self.list_view.selectedItems()
        selected_indexes = [self.list_view.indexFromItem(sel).row() for sel in selected]
        selected_indexes.sort()
        sel_count = len(selected_indexes)
        if len(selected_indexes) > 0 and selected_indexes[sel_count - 1] < self.list_view.count() - 1:
            for i_index in range(sel_count):
                next_item = self.list_view.takeItem(selected_indexes[sel_count - i_index - 1] + 1)
                self.list_view.insertItem(selected_indexes[sel_count - i_index - 1], next_item)
            self.status_bar.showMessage("Move " + str(len(selected_indexes)) + " items")
        else:
            self.status_bar.showMessage("Nothing to move")

    def click_invert(self):
        selected = self.list_view.selectedItems()
        selected_indexes = []
        for sel in selected:
            selected_indexes.append(self.list_view.indexFromItem(sel).row())
        total_indexes = [i for i in range(self.list_view.count())]
        new_indexes = []
        for i in total_indexes:
            if i not in selected_indexes:
                new_indexes.append(i)
        self.list_view.clearSelection()
        for i in new_indexes:
            self.list_view.item(i).setSelected(True)
        self.status_bar.showMessage("Invert selection: " + str(new_indexes))

    def click_delete(self):
        selected = self.list_view.selectedItems()
        delete_names = []
        for s in selected:
            s_index = self.list_view.indexFromItem(s).row()
            del_item = self.list_view.takeItem(s_index)
            delete_names.append(del_item.text())
        if len(delete_names) == 0:
            self.status_bar.showMessage("Nothing to delete")
        else:
            self.status_bar.showMessage("Delete items: " + ", ".join(delete_names))

    def click_add_files(self):
        files_dialog = QFileDialog()
        files_dialog.setNameFilter("Images (*.jpg *.jpeg *.bmp *.png *.tiff)")
        files_dialog.setFileMode(QFileDialog.ExistingFiles)
        if files_dialog.exec_():
            files = files_dialog.selectedFiles()
            self.add_items(files)
