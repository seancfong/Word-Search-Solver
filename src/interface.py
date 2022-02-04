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
        self._root_window.bind('<Configure>', image_updater(self))

        self._image_object = None
        self._canvas = tkinter.Canvas(width=300, height=200, bg='black')

        self._canvas.bind('<Button-1>', image_draw_begin(self))

        self._open_button = tkinter.Button(
            self._root_window, text='Open Image', command=self._open_image
        )
        self._open_button.grid(
            row=0, column=0
        )
        self._canvas.grid(
            row=0, column=1,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )


    def _convert_image(self) -> 'PhotoImage':
        '''
        Converts the cv2 image into a format supported by Tkinter to display
        '''
        # convert cv2 image to PIL
        to_display = Image.fromarray(self._image_object.get_image())

        # resize image
        img_width, img_height = self._image_object.get_image_dimensions()
        window_height = self._root_window.winfo_height()
        to_display = to_display.resize((window_height * img_width // img_height, window_height))
        # resize canvas
        self._canvas.configure(width=(window_height * img_width // img_height), height=window_height)

        # shapes
        self._bounding_box = None

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
        self._update_image()


    def _update_image(self) -> None:
        '''
        Updates the image by calling the higher order function image_updater
        '''
        image_updater(self)()


    def canvas_to_img(self, canvas_x, canvas_y) -> (int, int):
        '''
        Converts canvas coordinates to image coordinates
        '''
        img_width, img_height = self._image_object.get_image_dimensions()
        self._canvas.update()
        canvas_width, canvas_height = self._canvas.winfo_width(), self._canvas.winfo_height()
        return math.ceil(canvas_x / canvas_width * img_width), math.ceil(canvas_y / canvas_height * img_height)


    def run(self) -> None:
        '''
        Runs the main loop
        '''
        self._root_window.mainloop()


###############################################
# Higher Order Functions

def image_draw_begin(self) -> callable:
    def _begin_draw(event) -> None:
        '''
        Begins a point for the drawing
        '''
        print(event, self.canvas_to_img(event.x, event.y))
        if not self._bounding_box:
            self._bounding_box = self._canvas.create_oval(event.x, event.y, event.x+10, event.y+10)
        else:
            self._canvas.coords(self._bounding_box, event.x, event.y, event.x+10, event.y+10)

    return _begin_draw


def image_updater(self) -> callable:
    def _update(event=None) -> None:
        '''
        Updates the current image displayed
        '''
        if self._image_object:
            # update the image
            to_display = self._convert_image()

            # update the image panel
            self._canvas.create_image(0, 0, image=to_display, anchor=tkinter.NW)
            # set an attribute to the label in order for the image to render correctly
            self._canvas.image = to_display

    return _update


if __name__ == '__main__':
    SolverApp().run()