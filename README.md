
# Word Search Solver - wsvision 

A word-recognition application written in Python that identifies and displays solutions for 
any image of a word search puzzle. Used with OpenCV and PyTesseract.

## Demonstrations

### Opening image of word search puzzle 

![Word Highlighter](/src/media/open_and_scan_2_v2_0_1.gif?raw=true "Word Highlighter")

### Displaying scanned words

![Word Highlighter](/src/media/word_display_2_v2_0_1.gif?raw=true "Word Highlighter")

GIF capture by https://gifcap.dev/


## Authors

- [@seancfong](https://www.github.com/seancfong)

# Getting Started
To try this out for yourself, please refer to the following installation guide:

## 1. Clone the repository
Start by entering the following command:

```bash
git clone https://github.com/seancfong/Word-Search-Solver.git
```

Then in a command line terminal, navigate to the root directory of the repository and start the Python virtual environment:

```bash
/virtual_env/Scripts/activate.bat  # command line
/virtual_env/Scripts/Activate.ps1  # powershell
```

## 2. Install required dependencies
With the virtual environment activated, install the packages listed in ```requirements.txt```.

```bash
pip install -r requirements.txt
```

## 3. Install Tesseract
This application relies on Google's Tesseract OCR to scan and process text from images. You can read more about the installation guide [here](https://tesseract-ocr.github.io/tessdoc/Installation.html).

Note that this application is intended to be used with English training data. The tesseract directory should also be located in ```C:\Program Files\Tesseract-OCR\```.

## 4. Enjoy!
You should now be able to run the program with the following command in ```/src```.

```bash
python main.py
```

## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)