import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QListWidget, QAbstractItemView, QVBoxLayout, QPushButton, QFileDialog
from PySide2.QtCore import Qt
from PyPDF2 import PdfFileReader
from processor_widgets import SelectWidget, ImageListItem


class SynthPdfWidget(QWidget):
    def __init__(self, status_bar):
        super(SynthPdfWidget, self).__init__()
        self.status_bar = status_bar
        layout = QHBoxLayout()
        self.list_view = QListWidget()
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.itemClicked.connect(self.click_item_signal)
        self.list_view.itemEntered.connect(self.click_item_signal)
        self.list_view.itemSelectionChanged.connect(self.change_selection_signal)

        controls_layout = QVBoxLayout()
        controls_layout.setAlignment(Qt.AlignTop)

        select_zone = SelectWidget(self.click_move_up, self.click_move_down, self.click_invert, self.click_delete)
        select_zone.setMinimumWidth(250)

        add_pages_button = QPushButton("Add Pages From PDF")
        add_pages_button.clicked.connect(self.add_pdf)

        controls_layout.addWidget(select_zone)
        controls_layout.addWidget(add_pages_button)

        layout.addWidget(self.list_view)
        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def _add_pages_from_pdf(self, pdf_path):
        with open(pdf_path, "rb") as file:
            reader = PdfFileReader(file)
            file_name = os.path.basename(pdf_path)
            pages_count = reader.getNumPages()
            for i in range(pages_count):
                new_item = ImageListItem("page " + str(i + 1) + " (" + file_name + ")", (pdf_path, i))
                self.list_view.addItem(new_item)
            self.status_bar.showMessage("Add " + str(pages_count) + " pages")

    # ----------external methods from create command
    def extern_get_files_and_pages(self):  # return selected pages in the form {file1: [p1, p2, ...], file2: [p1, p2, ...], ...}
        to_return = {}
        if len(self.list_view.selectedItems()) == 0:  # nothing selected, add all pages
            items_count = self.list_view.count()
            for item_index in range(items_count):
                item = self.list_view.item(item_index)
                item_data = item.get_data()
                file_name = item_data[0]
                page_index = item_data[1]
                if file_name in to_return:
                    to_return[file_name].append(page_index)
                else:
                    to_return[file_name] = [page_index]
        else:
            for s in self.list_view.selectedItems():
                s_data = s.get_data()
                file_name = s_data[0]
                page_index = s_data[1]
                if file_name in to_return:
                    to_return[file_name].append(page_index)
                else:
                    to_return[file_name] = [page_index]
        return to_return

    # ----------add button-----------------------
    def add_pdf(self):
        files_dialog = QFileDialog()
        files_dialog.setNameFilter("PDF (*.pdf)")
        files_dialog.setFileMode(QFileDialog.ExistingFiles)
        if files_dialog.exec_():
            files = files_dialog.selectedFiles()
            for f_path in files:
                self._add_pages_from_pdf(f_path)

    # ----------List_view signals----------------
    def click_item_signal(self, item):
        self.status_bar.showMessage("Select " + str(item.text()))

    def change_selection_signal(self):
        if len(self.list_view.selectedItems()) == 0:
            # self._set_preview(None)  # nothing selected
            pass

    # ----------list_view commands---------------
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
