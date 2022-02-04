'''
The interface.py module implements functionality for creating
a user interface to import and view solvable puzzles
'''

import imaging
import math
import tkinter
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog

class SolverApp:
    def __init__(self) -> None:
        self._root_window = tkinter.Tk()
        self._root_window.title('Word Search')
        self._root_window.geometry('800x600')
        self._root_window.minsize(width=300, height=300)
        self._root_window.bind('<Configure>', image_resizer(self))
        self._image_object = None
        self._image_panel = tkinter.Label()
        self._open_button = tkinter.Button(
            self._root_window, text='Open Image', command=self._open_image
        )
        self._open_button.grid(
            row=0, column=0
        )
        self._image_panel.grid(
            row=0, column=1,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )

    def _convert_image(self) -> 'PhotoImage':
        '''
        Converts the cv2 image into a format supported by Tkinter to display
        '''
        # convert cv2 image to PIL
        to_display = Image.fromarray(self._image_object.get_image())
        img_width, img_height = map(math.ceil, self._image_object.get_image_dimensions())
        window_height = self._root_window.winfo_height()
        to_display = to_display.resize((window_height * img_width // img_height, window_height))
        # convert PIL image to ImageTk
        to_display = ImageTk.PhotoImage(to_display)
        return to_display


    def _open_image(self) -> None:
        '''
        Prompts the user to select and image and
        displays it in the interface
        '''
        # prompt user to open an image
        path = filedialog.askopenfilename()
        # update current image
        self._image_object = imaging.Imaging(path)
        image_resizer(self)()


    def run(self) -> None:
        '''
        Runs the main loop
        '''
        self._root_window.mainloop()


def image_resizer(self):
    def _update_image(*event) -> None:
        '''
        Updates the current image displayed
        '''
        # update the image
        to_display = self._convert_image()

        # update the image panel
        self._image_panel.configure(image=to_display)
        # set an attribute to the label in order for the image to render correctly
        self._image_panel.image = to_display

    return _update_image


if __name__ == '__main__':
    SolverApp().run()