'''
The interface.py module implements functionality for creating
a user interface to import and view solvable puzzles
'''

import imaging
import math
import tkinter
import search
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
        self._wordsearch_info = None
        self._wordsearch_content = []
        self._wordbank_info = None
        self._wordsearch_results = None
        self._wordbank_results = None
        self._wordsearch_on_img = None
        self._wordbank_on_img = None

        # for solutions
        self._word_select_list = tkinter.Listbox(
            self._sidebar_bottom, selectmode=tkinter.MULTIPLE
        )
        self._answer_dict = dict()
        self._puzzle_origin = None
        self._puzzle_unit_x = None
        self._puzzle_unit_y = None
        self._answer_marking_dict = dict()

        # buttons
        self._autosolve_mode = tkinter.Button(
            self._menu, text='Word Search Solver'
        )
        self._open_button = tkinter.Button(
            self._sidebar, text='Open Image', command=self._open_image
        )
        self._process_button = tkinter.Button(
            self._sidebar, text='Solve', command=self._solve_puzzle
        )
        self._puzzle_select_button = tkinter.Button(
            self._sidebar, text='Select Word Search', command=self._begin_wordsearch_select
        )
        self._word_bank_select_button = tkinter.Button(
            self._sidebar, text='Select Word Bank', command=self._begin_wordbank_select
        )
        self._redo_select_button = tkinter.Button(
            self._sidebar_bottom, text='Redo Selection', command=self._reset_select
        )
        self._confirm_wordsearch_button = tkinter.Button(
            self._sidebar_bottom, text='Confirm Selection', command=self._confirm_wordsearch_selection
        )
        self._confirm_wordbank_button = tkinter.Button(
            self._sidebar_bottom, text='Confirm Selection', command=self._confirm_wordbank_selection
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
            self._begin_wordsearch_select_mode()

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

    def img_to_canvas(self, img_x, img_y, rounding=True) -> (int, int):
        '''
        Converts image coordinates to canvas coordinates
        '''
        img_width, img_height = self._image_object.get_image_dimensions()
        self._canvas.update()
        canvas_width, canvas_height = self._canvas.winfo_width(), self._canvas.winfo_height()
        if rounding:
            return math.floor(img_x / img_width * canvas_width), math.ceil(img_y / img_height * canvas_height)
        return img_x / img_width * canvas_width, img_y / img_height * canvas_height

    def _begin_wordsearch_select_mode(self) -> None:
        '''
        Updates interface for autosolve mode
        '''
        self._puzzle_select_button.grid(
            row=1, column=0, sticky='nesw'
        )
        self._word_bank_select_button.grid(
            row=2, column=0, sticky='nesw'
        )

    def _end_selection(self) -> None:
        '''
        Ends the selection mode
        '''
        # remove drawing
        self._canvas.delete('bounding-box')
        # remove event bindings
        self._canvas.unbind('<Button-1>')
        self._canvas.unbind('<B1-Motion>')
        self._canvas.unbind('<ButtonRelease-1>')

    def _begin_wordsearch_select(self) -> None:
        '''
        Begins the wordsearch selector by binding events to the canvas
        '''
        self._reset_select()
        # bind events to canvas
        self._canvas.bind('<Button-1>', bounding_box_begin(self))
        self._canvas.bind('<B1-Motion>', bounding_box_edit(self))
        self._canvas.bind('<ButtonRelease-1>', bounding_box_finish(self))
        # edit buttons
        self._redo_select_button.grid(
            row=0, column=0, sticky='nesw'
        )
        self._confirm_wordsearch_button.grid(
            row=1, column=0, sticky='nesw'
        )

    def _reset_select(self) -> None:
        '''
        Resets the selection process for the bounding box
        '''
        if self._bounding_box:
            self._bounding_box = None
            self._canvas.delete('bounding-box')

    def _confirm_wordsearch_selection(self) -> None:
        '''
        Confirms the wordsearch puzzle is selected
        '''
        self._end_selection()
        # remove selection buttons
        self._puzzle_select_button['state'] = tkinter.DISABLED
        self._redo_select_button.grid_forget()
        self._confirm_wordsearch_button.grid_forget()
        self._wordsearch_info = self._bounding_box
        self._wordsearch_on_img = self.canvas_to_img(self._bounding_box.get_x(), self._bounding_box.get_y())
        self._bounding_box = None
        self._check_to_solve()

    def _begin_wordbank_select(self) -> None:
        '''
        Begins selection for the word bank
        '''
        self._reset_select()
        # bind events to canvas
        self._canvas.bind('<Button-1>', bounding_box_begin(self))
        self._canvas.bind('<B1-Motion>', bounding_box_edit(self))
        self._canvas.bind('<ButtonRelease-1>', bounding_box_finish(self))
        # edit buttons
        self._redo_select_button.grid(
            row=0, column=0, sticky='nesw'
        )
        self._confirm_wordbank_button.grid(
            row=1, column=0, sticky='nesw'
        )

    def _confirm_wordbank_selection(self) -> None:
        '''
        Confirms the word bank is selected
        '''
        self._end_selection()
        # remove selection buttons
        self._word_bank_select_button['state'] = tkinter.DISABLED
        self._redo_select_button.grid_forget()
        self._confirm_wordbank_button.grid_forget()
        self._wordbank_info = self._bounding_box
        self._wordbank_on_img = self.canvas_to_img(self._bounding_box.get_x(), self._bounding_box.get_y())
        self._bounding_box = None
        self._check_to_solve()

    def _check_to_solve(self) -> None:
        '''
        Checks whether puzzle has enough data to be solved
        '''
        if self._wordsearch_info and self._wordbank_info:
            self._process_button.grid(
                row=3, column=0
            )

    def _solve_puzzle(self) -> None:
        '''
        Solves the puzzle with all the data from image scanned
        '''
        # remove buttons
        self._process_button.grid_forget()
        self._word_bank_select_button.grid_forget()
        self._puzzle_select_button.grid_forget()

        # insert listbox
        self._word_select_list.grid(
            row=0, column=0
        )

        # wordsearch section
        x1, y1 = self._wordsearch_info.get_x(), self._wordsearch_info.get_y()
        x2, y2 = self._wordsearch_info.get_end_x(), self._wordsearch_info.get_end_y()
        # print(x1, y1, x2, y2)
        self._wordsearch_results = self._image_object.process_selection(
            self.canvas_to_img(x1, y1), self.canvas_to_img(x2, y2),
            config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ1')

        # create a 2-D list with the current data
        self._wordsearch_content = []
        sum_width = 0
        sum_height = 0
        y_count = 0
        x_count = 0
        for result in self._wordsearch_results:
            line_as_char = list(result.char)
            self._wordsearch_content.append(line_as_char)
            y_count += 1
            if x_count == 0:
                x_count = len(line_as_char)
            elif len(line_as_char) != x_count:
                print('discrepancy found in line lengths')

            sum_width += result.w
        sum_height = self._wordsearch_results[-1].y + self._wordsearch_results[-1].h - self._wordsearch_results[0].y

        print(sum_width, sum_height)
        self._puzzle_unit_x, self._puzzle_unit_y = self.img_to_canvas(sum_width / x_count ** 2, sum_height / y_count, rounding=False)
        print('units', self._puzzle_unit_x, self._puzzle_unit_y)

        print(self._wordsearch_content)

        # wordbank section
        x1, y1 = self._wordbank_info.get_x(), self._wordbank_info.get_y()
        x2, y2 = self._wordbank_info.get_end_x(), self._wordbank_info.get_end_y()
        # print(x1, y1, x2, y2)
        self._wordbank_results = self._image_object.process_selection(
            self.canvas_to_img(x1, y1), self.canvas_to_img(x2, y2),
            config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1')

        # solve the wordsearch
        searcher = search.Searcher(self._wordsearch_content)

        # insert words into word list
        for index, result in enumerate(self._wordbank_results):
            word = result.char
            self._word_select_list.insert(index, word)
            self._answer_dict[word] = searcher.search(word)

        self._word_select_list.bind('<<ListboxSelect>>', _word_selector(self))

    def draw_solution(self, word):
        '''
        Draws a solution for the given word
        '''
        # update puzzle units
        self._create_puzzle_units()
        origin_x, origin_y = self._puzzle_origin[0], self._puzzle_origin[1]
        found_search_list = self._answer_dict[word]
        for fs in found_search_list:
            print(fs.r, fs.c)
            x1, y1 = origin_x + (self._puzzle_unit_x * fs.c), origin_y + (self._puzzle_unit_y * fs.r)
            x2, y2 = x1 + (fs.dx * (len(word) - 0.5) * self._puzzle_unit_x), y1 + \
                     (fs.dy * (len(word) - 0.5) * self._puzzle_unit_y)
            self._canvas.create_line(
                x1, y1, x2, y2,
                tags='solution-line-' + word, fill='blue', width=2)

    def _create_puzzle_units(self):
        '''
        Creates units on puzzle image to simplify drawing
        '''
        # puzzle origin is first item in wordsearch results
        # find origin of the selected image and convert to canvas coords
        cropped_origin_x, cropped_origin_y = self.img_to_canvas(self._wordsearch_results[0].x,
                                                                self._wordsearch_results[0].y)
        # find origin of the wordsearch info and convert to canvas coords
        wordsearch_origin_x, wordsearch_origin_y = self.img_to_canvas(*self._wordsearch_on_img)
        self._puzzle_origin = cropped_origin_x + wordsearch_origin_x + self._puzzle_unit_x * 0.5, \
                              cropped_origin_y + wordsearch_origin_y + self._puzzle_unit_y * 0.5
        print('origin', self._puzzle_origin)

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


def _word_selector(self) -> callable:
    def _select(event=None) -> None:
        '''
        Handles the selection of a word
        '''
        selections = event.widget.curselection()
        print(selections)
        for index in selections:
            selection_name = event.widget.get(index)  # returns the indices selected in the listbox
            # solve this data
            print(self._answer_dict[selection_name])
            try:
                self.draw_solution(selection_name)
            except Exception as e:
                print(e)
                print('Failed to draw solution')

    return _select


if __name__ == '__main__':
    SolverApp().run()
