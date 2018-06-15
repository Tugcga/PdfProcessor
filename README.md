# PDF Processor

Python based application for creating and modifying pdf-files. It can create pdf from set of images. Also it can extract pages from other pdf-files and union different files. You can select some pages from one file, some from the other and save it to the separate file. To run the program execute

```
python pdf_processor.py
```

Require modules:
* PySide2
* Pillow
* PyPDF2
* reportlab

## Image to Pdf

![Image to Pdf window](screen_01.png?raw=true)

1. Add files to the list by pressing "Add Files button
2. Reorange files in the list by clicking buttons on the Selection section
3. Choose save mode in the Options section. "From Source" will create pdf with separate pages of different size (depend of the image size and proportions). "A4" will create pdf with A4-pages and images fitted to this size.
4. Press "Create Pdf" button to save images to pdf file.

## Synthesize Pdf

![Synth Pdf window](screen_02.png?raw=true)

1. Add pages of the pdf file by pressinf "Add Pages From PDF" button.
2. Reorange pages by clicking buttons on the Selection section.
3. Select some pages and press "Create PDF". It will create pdf with only selected pages. If nothing selected, then all pages on the list will be saved.