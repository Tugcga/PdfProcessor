import sys
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QSlider, QHBoxLayout, QComboBox, QColorDialog
from PySide2.QtGui import QColor, QPainter, QPen
from PySide2.QtCore import Qt


class ParameterInteger(QWidget):
    def check_int(self, s):
        if s[0] in ("-", "+"):
            return s[1:].isdigit()
        return s.isdigit()

    def clamp(self, value, min_value, max_value):
        if value < min_value:
            return min_value
        elif value > max_value:
            return max_value
        else:
            return value

    def __init__(self, parent=None, value=0, name="", label_text="", min_value=None, max_value=None, label_width=64, height=22, min_visible=0, max_visible=10, change_callback=None):
        QWidget.__init__(self, parent)

        self.VERTICAL_MARGIN = 0
        self.HORIZONTAL_MARGIN = 0

        self.name = name
        self.label_text = label_text
        self.min_value_raw = min_value
        self.max_value_raw = max_value
        self.min_value = min_value if min_value is not None else -sys.maxsize
        self.max_value = max_value if max_value is not None else sys.maxsize
        self.value = self.clamp(value, self.min_value, self.max_value)
        self.min_visible = max(self.min_value, min(min_visible, self.value))
        self.max_visible = min(self.max_value, max(max_visible, self.value))
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)
        self.value_textbox = QLineEdit()
        self.value_textbox.setFixedWidth(52)
        self.value_textbox.setFixedHeight(height)
        self._update_value_label()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFixedHeight(height)
        self._update_visible_interval()
        self.slider.setValue(value)
        layout = QHBoxLayout()
        layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        layout.addWidget(self.label)
        layout.addWidget(self.value_textbox)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.slider_valueChanged)
        self.value_textbox.returnPressed.connect(self.textbox_enter)
        self.value_textbox.editingFinished.connect(self.textbox_enter)
        self.slider.sliderReleased.connect(self.slider_sliderReleased)

    def _update_visible_interval(self):
        self.slider.setRange(self.min_visible, self.max_visible)

    def _update_value_label(self):
        self.value_textbox.setText(str(self.value))

    def slider_valueChanged(self, value):
        self.value = value
        self._update_value_label()
        self.value_change()

    def slider_sliderReleased(self):
        self.try_change_visible(self.value)
        self.slider.setValue(self.value)

    def try_change_visible(self, new_value):
        delta = self.max_visible - self.min_visible
        # increase visible interval if new value out of the current
        if new_value <= self.min_visible:
            self.min_visible = max(self.min_value, new_value - delta)
        if new_value >= self.max_visible:
            self.max_visible = min(self.max_value, new_value + delta)
        self._update_visible_interval()

    def textbox_enter(self):
        text = self.value_textbox.text()
        # check is this text is integer
        if self.check_int(text):
            new_value = int(text)
            # clamp value
            if new_value < self.min_value:
                new_value = self.min_value
            if new_value > self.max_value:
                new_value = self.max_value
            self.try_change_visible(new_value)
            self.slider.setValue(new_value)
            self._update_value_label()
            self.value_change()
        else:
            self._update_value_label()
        self.value_textbox.clearFocus()

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)


class ParameterCombobox(QWidget):
    def __init__(self, parent=None, value=0, items=[], name="", label_text="", label_width=64, height=22, change_callback=None):
        QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 0
        self.HORIZONTAL_MARGIN = 0

        self.name = name
        self.label_text = label_text
        self.value = value
        self._items = [item for item in items]
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None

        self.label = QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)

        self.value_combobox = QComboBox()
        self.value_combobox.addItems(items)
        self.value_combobox.setCurrentIndex(self.value)
        self.value_combobox.currentIndexChanged.connect(self.selection_changed)
        self.value_combobox.setFixedHeight(height)
        self.value_combobox.setMinimumWidth(24)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_combobox, 1)
        self.setLayout(self.layout)

    def selection_changed(self, index):
        self.value = index
        self.value_change()

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=(self.value, self._items))


class ParameterColor(QWidget):
    def __init__(self, parent=None, value=QColor(128, 128, 128, 255), name="", label_text="", label_width=64, height=22, change_callback=None):
        QWidget.__init__(self, parent)
        self.VERTICAL_MARGIN = 0
        self.HORIZONTAL_MARGIN = 0

        self.name = name
        self.label_text = label_text
        self.value = value
        self._is_callback_define = False
        if change_callback is not None:
            self._change_callback = change_callback
            self._is_callback_define = True
        self._last_call = None
        self._color_height = 16
        self._label_to_color_gap = 6
        self._right_margin = 1
        self._color_width = None

        # calculate color rectangle zone
        self._color_rect_min_x = label_width + self._label_to_color_gap
        self._color_rect_min_y = None

        self.label = QLabel(label_text)
        self.label.setFixedWidth(label_width)
        self.label.setFixedHeight(height)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN, self.HORIZONTAL_MARGIN, self.VERTICAL_MARGIN)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        size = self.size()  # the size of allowed are for the widget
        self._color_rect_min_y = (size.height() - self._color_height) // 2
        self._color_width = size.width() - self._color_rect_min_x - self._right_margin
        painter = QPainter()
        painter.begin(self)
        border_pen = QPen()
        border_pen.setColor(QColor(122, 122, 122))
        painter.setPen(border_pen)
        painter.setBrush(self.value)

        painter.drawRect(self._color_rect_min_x, self._color_rect_min_y, self._color_width, self._color_height)
        painter.end()

    def mousePressEvent(self, event):
        pos = event.pos()
        # check is we click to the color area
        x = pos.x()
        y = pos.y()
        if self._color_rect_min_y is not None and self._color_width is not None:
            if x > self._color_rect_min_x and x < self._color_rect_min_x + self._color_width and y > self._color_rect_min_y and y < self._color_rect_min_y + self._color_height:
                color = QColorDialog.getColor(initial=self.value)
                if color.isValid():
                    self.value = QColor(color.red(), color.green(), color.blue())
                    self.value_change()
                    self.repaint()

    def value_change(self):
        if self._is_callback_define:
            if self._last_call is None or self._last_call != self.value:
                self._last_call = self.value
                self._change_callback(param_name=self.name, param_value=self.value)
