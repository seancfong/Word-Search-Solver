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
from geometry import Geometry


class SolverApp:
    def __init__(self) -> None:
        # root window
        self._root_window = tkinter.Tk()
        self._root_window.title('Word Search')
        self._root_window.geometry('800x600')
        self._root_window.minsize(width=300, height=300)
        self._root_window.bind('<Configure>', image_updater(self))

        # menu frames
        self._menu = tkinter.Frame()
        self._sidebar = tkinter.Frame()
        self._sidebar_bottom = tkinter.Frame()

        # canvas
        self._canvas = tkinter.Canvas(width=300, height=200, bg='black')
        self._bounding_box = None
        self._image_object = None
        self._crossword_info = None

        # buttons
        self._autosolve_mode = tkinter.Button(
            self._menu, text='Crossword Solver'
        )
        self._open_button = tkinter.Button(
            self._sidebar, text='Open Image', command=self._open_image
        )
        self._process_button = tkinter.Button(
            self._sidebar, text='Solve', command=self._solve_puzzle
        )
        self._puzzle_select_button = tkinter.Button(
            self._sidebar, text='Select Crossword', command=self._begin_crossword_select
        )
        self._redo_select_button = tkinter.Button(
            self._sidebar_bottom, text='Redo Selection', command=self._redo_select
        )

        # initialize positions
        self._menu.grid(
            row=0, column=0
        )
        self._canvas.grid(
            row=0, column=1, rowspan=2,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )
        self._sidebar.grid(
            row=0, column=2
        )
        self._sidebar_bottom.grid(
            row=1, column=2
        )

        self._open_button.grid(
            row=0, column=0, sticky='nesw'
        )
        self._process_button.grid(
            row=2, column=0, sticky='nesw'
        )
        self._autosolve_mode.grid(
            row=0, column=0, sticky='n'
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

        # convert PIL image to ImageTk
        to_display = ImageTk.PhotoImage(to_display)
        return to_display


    def _open_image(self) -> None:
        '''
        Prompts the user to select and image and
        displays it in the interface
        '''
        try:
            # prompt user to open an image
            path = filedialog.askopenfilename()
            # update current image
            self._image_object = imaging.Imaging(path)
            self._update_image()
        except Exception as e:
            print(e)
        else:
            self._begin_crossword_select_mode()


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


    def _begin_crossword_select_mode(self) -> None:
        '''
        Updates interface for autosolve mode
        '''
        self._puzzle_select_button.grid(
            row=1, column=0, sticky='nesw'
        )

    def _begin_crossword_select(self) -> None:
        '''
        Begins the crossword selector by binding events to the canvas
        '''
        # bind events to canvas
        self._canvas.bind('<Button-1>', bounding_box_begin(self))
        self._canvas.bind('<B1-Motion>', bounding_box_edit(self))
        self._canvas.bind('<ButtonRelease-1>', bounding_box_finish(self))
        # edit buttons
        self._puzzle_select_button.configure(text='Confirm', command=self._confirm_crossword_selection)
        self._redo_select_button.grid(
            row=0, column=0, sticky='nesw'
        )

    def _redo_select(self) -> None:
        '''
        Redoes the selection process for the bounding box
        '''
        if self._bounding_box:
            self._bounding_box = None
            self._canvas.delete('bounding-box')


    def _confirm_crossword_selection(self) -> None:
        '''
        Confirms the crossword puzzle is selected
        '''
        # remove drawing
        self._canvas.delete('bounding-box')
        # remove event bindings
        self._canvas.unbind('<Button-1>')
        self._canvas.unbind('<B1-Motion>')
        self._canvas.unbind('<ButtonRelease-1>')
        # remove selection buttons
        self._redo_select_button.grid_forget()
        self._crossword_info = self._bounding_box


    def _solve_puzzle(self) -> None:
        '''
        Solves the puzzle with all the data from image scanned
        '''
        # crossword section
        x1, y1 = self._crossword_info.get_x(), self._crossword_info.get_y()
        x2, y2 = self._crossword_info.get_end_x(), self._crossword_info.get_end_y()
        print(x1, y1, x2, y2)
        self._image_object.crop_selection(self.canvas_to_img(x1, y1), self.canvas_to_img(x2, y2))


    def run(self) -> None:
        '''
        Runs the main loop
        '''
        self._root_window.mainloop()


###############################################
# Higher Order Functions

def bounding_box_begin(self) -> callable:
    def _begin_draw(event) -> None:
        '''
        Begins a point for the bounding box
        '''
        if not self._bounding_box:
            box = self._canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                tags='bounding-box', outline='blue', width=2)

            # create new Geometry object
            self._bounding_box = Geometry(box, event.x, event.y)

    return _begin_draw

def bounding_box_edit(self) -> callable:
    def _edit_draw(event) -> None:
        '''
        Edits the dimensions of the bounding box
        '''
        if self._bounding_box and self._bounding_box.is_drawable():
            # update the coordinates of current drawing shape
            self._canvas.coords(self._bounding_box.get_shape(),
                                self._bounding_box.get_x(), self._bounding_box.get_y(), event.x, event.y)

    return _edit_draw

def bounding_box_finish(self) -> callable:
    def _finish_draw(event) -> None:
        '''
        Finish drawing the bounding box
        '''
        if self._bounding_box:
            # set the endpoints of the bounding box
            self._bounding_box.set_end_x(event.x)
            self._bounding_box.set_end_y(event.y)
            self._bounding_box.set_drawable(False)
            print(self._bounding_box.get_x(), self._bounding_box.get_y(), event.x, event.y)

    return _finish_draw


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