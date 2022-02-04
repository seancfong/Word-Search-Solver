'''
The imaging.py module implements functionality for reading images
and extracting textual data using pytesseract and OpenCV
'''
import math

import pytesseract
import cv2

# Configuration for pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class Imaging:
    def __init__(self, img: str) -> None:
        # read the image
        self._image = cv2.imread(img)
        # convert image to rgb
        self._image = cv2.cvtColor(self._image, cv2.COLOR_BGR2RGB)
        # get the height and width of image
        self._image_height, self._image_width, _ = self._image.shape

    def get_image(self) -> 'Image':
        return self._image

    def get_image_dimensions(self) -> (int, int):
        '''
        Returns the dimensions of the image as a tuple of integers
        '''
        return self._image_width, self._image_height




# For testing the module
if __name__ == '__main__':
    imager = Imaging('example_1.jpg')
    cv2.imshow('Test image', imager.get_image())
    cv2.waitKey(0)

