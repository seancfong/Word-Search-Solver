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
    def __init__(self, img: str):
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

    def crop_selection(self, coord1, coord2):
        x1, y1 = coord1
        x2, y2 = coord2
        print(x1, y1, x2, y2)
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        cropped_img = self._image[y1:y2, x1:x2]
        cv2.imshow('Test image', cropped_img)


# For testing the module
if __name__ == '__main__':
    # 49 89 393 415
    imager = Imaging('example_1.jpg')
    cv2.imshow('Test image', imager.get_image())
    cv2.waitKey(0)

