'''
The imaging.py module implements functionality for reading images
and extracting textual data using pytesseract and OpenCV
'''
from collections import namedtuple
import pytesseract
import cv2


class TextData:
    def __init__(self, char, x, y, w, h, conf):
        self.char = char
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.conf = conf


# Configuration for pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
_DEFAULT_CONFIG = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1'

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

    def _crop_selection(self, coord1, coord2) -> 'Image':
        x1, y1 = coord1
        x2, y2 = coord2
        # print(x1, y1, x2, y2)
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        return self._image[y1:y2, x1:x2].copy()


    def process_selection(self, coord1, coord2, config=_DEFAULT_CONFIG):
        cropped_img = self._crop_selection(coord1, coord2)
        all_data = []

        for i, b in enumerate(pytesseract.image_to_data(cropped_img, config=config).splitlines()):
            # print(b)
            if i != 0:
                b = b.split()
                if len(b) == 12:
                    x, y, w, h = map(int, b[6:10])
                    char = b[-1]
                    conf = float(b[10])
                    cv2.rectangle(cropped_img, (x, y), (w + x, h + y), (0, 0, 255), 2)
                    cv2.putText(cropped_img, char, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (50, 50, 255), 2)
                    all_data.append(TextData(x=x, y=y, w=w, h=h, char=char, conf=conf))

        # print(all_data)
        # cv2.imshow('Test image', cropped_img)
        # cv2.waitKey(0)
        return all_data


# For testing the module
if __name__ == '__main__':
    # 49 89 393 415
    imager = Imaging('example_1.jpg')
    # cv2.imshow('Test image', imager.get_image())
    # cv2.waitKey(0)
    imager.process_selection((55, 107), (531, 565))
    cv2.waitKey(0)

