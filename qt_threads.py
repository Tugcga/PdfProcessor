from PySide2.QtCore import QThread, Signal
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, A5, A6
from PIL import Image


class CreatePdfPagesThread(QThread):
    step_signal = Signal(object)
    message_signal = Signal(object)

    def __init__(self, file_path, pages_dict):
        super(CreatePdfPagesThread, self).__init__()
        self.file_path = file_path
        self.pages_dict = pages_dict
        self.total_pages = 0
        for f, p_array in self.pages_dict.items():
            self.total_pages += len(p_array)

    def run(self):
        writer = PdfFileWriter()
        iterator = 0
        for pdf_path, pages_array in self.pages_dict.items():
            file = open(pdf_path, "rb")
            pdf = PdfFileReader(file)
            for p in pages_array:
                self.step_signal.emit((iterator + 1, self.total_pages))
                writer.addPage(pdf.getPage(p))
        with open(self.file_path, "wb") as output_stream:
            self.message_signal.emit("Save file " + self.file_path)
            writer.write(output_stream)


class CreatePdfThread(QThread):
    step_signal = Signal(object)
    message_signal = Signal(object)

    def __init__(self, file_path, data):
        QThread.__init__(self)
        self.file_path = file_path
        self.img_data = data

    def run(self):
        mode = self.img_data[1]["mode"]
        canv = canvas.Canvas(self.file_path)
        pages = len(self.img_data[0])
        for i in range(pages):
            self.step_signal.emit((i + 1, pages))
            img_path = self.img_data[0][i]
            width = None
            height = None
            with Image.open(img_path) as img:
                size = img.size
                width = size[0]
                height = size[1]
            margin = self.img_data[1]["margin"]
            background = self.img_data[1]["background"]
            if mode == 0:
                pixels = self.img_data[1]["pixels"]
                page_width = width + 2 * margin
                page_height = height + 2 * margin
                canv.setPageSize((page_width / pixels, page_height / pixels))
                if margin > 0:
                    canv.setFillColorRGB(background[0] / 255, background[1] / 255, background[2] / 255)
                    canv.rect(0, 0, page_width, page_height, stroke=0, fill=1)
                canv.drawImage(img_path, margin / pixels, margin / pixels, width / pixels, height / pixels)
            else:
                img_prop = height / width
                page_width = A4[0] if mode == 1 else (A5[0] if mode == 2 else (A6[0] if mode == 3 else letter[0]))
                page_height = A4[1] if mode == 1 else (A5[1] if mode == 2 else (A6[1] if mode == 3 else letter[1]))
                page_prop = page_height / page_width
                img_width = page_width - 2*margin
                img_height = page_height - 2*margin
                if img_prop > page_prop:
                    img_width = img_height / img_prop
                else:
                    img_height = img_width * img_prop
                if mode == 1:  # A4
                    canv.setPageSize(A4)
                elif mode == 2:  # A5
                    canv.setPageSize(A5)
                elif mode == 3:  # A6
                    canv.setPageSize(A6)
                elif mode == 4:  # Letter
                    canv.setPageSize(letter)
                align = self.img_data[1]["align"]
                x_shift = 0
                y_shift = 0
                if align == 0:  # center
                    x_shift = (page_width - img_width) / 2
                    y_shift = (page_height - img_height) / 2
                elif align == 1:  # Top-Center
                    x_shift = (page_width - img_width) / 2
                    y_shift = page_height - img_height - margin
                elif align == 2:  # Bottom-Center
                    x_shift = (page_width - img_width) / 2
                    y_shift = margin
                elif align == 3:  # Left-Top
                    x_shift = margin
                    y_shift = page_height - img_height - margin
                elif align == 4:  # Left-Center
                    x_shift = margin
                    y_shift = (page_height - img_height) / 2
                elif align == 5:  # Left-Bottom
                    x_shift = margin
                    y_shift = margin
                elif align == 6:  # Right-Top
                    x_shift = page_width - img_width - margin
                    y_shift = page_height - img_height - margin
                elif align == 7:  # Right-Center
                    x_shift = page_width - img_width - margin
                    y_shift = (page_height - img_height) / 2
                elif align == 8:  # Right-Bottom
                    x_shift = page_width - img_width - margin
                    y_shift = margin
                if margin > 0:
                    canv.setFillColorRGB(background[0] / 255, background[1] / 255, background[2] / 255)
                    canv.rect(0, 0, page_width, page_height, stroke=0, fill=1)
                canv.drawImage(img_path, x_shift, y_shift, img_width, img_height)
            canv.showPage()
        self.message_signal.emit("Save file " + self.file_path)
        canv.save()
