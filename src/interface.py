'''
The interface.py module implements functionality for creating
a user interface to import and view solvable puzzles
'''

import imaging
import math
import tkinter
import search
import customtkinter
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import scrolledtext
from geometry import Geometry

class SolverApp:
    def __init__(self) -> None:
        # initialize custom Tkinter
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        # root window
        self._root_window = customtkinter.CTk()
        self._root_window.title('wsvision 2.0.1')
        self._root_window.geometry('1200x700')
        self._root_window.minsize(width=800, height=500)
        self._root_window.bind('<Configure>', image_updater(self))

        # font
        self._font_button = customtkinter.CTkFont(family="Calibri", size=18)
        self._font_mono = customtkinter.CTkFont(family="Consolas", size=16)

        # menu frames
        self._menu = customtkinter.CTkFrame(self._root_window)
        self._sidebar = customtkinter.CTkFrame(self._root_window, fg_color="#222222")
        self._sidebar_bottom = customtkinter.CTkFrame(self._root_window)
        self._sidebar_right_1 = customtkinter.CTkFrame(self._root_window)
        self._sidebar_right_2 = customtkinter.CTkFrame(self._root_window)
        self._sidebar_right_bottom = customtkinter.CTkFrame(self._root_window)

        # canvas
        self._canvas = tkinter.Canvas(width=500, height=700)
        self._bounding_box = None
        self._image_object = None
        self._wordsearch_info = None
        self._wordsearch_content = []
        self._wordbank_content = []
        self._wordbank_info = None
        self._wordsearch_results = None
        self._wordbank_results = None
        self._wordsearch_on_img = None
        self._wordbank_on_img = None
        self._welcome_image = customtkinter.CTkImage(Image.open('assets/welcome.png'), size=(400,500))
        self._welcome_image_label = customtkinter.CTkLabel(self._root_window, image=self._welcome_image, height=700, text="")


        # for solutions
        self._word_select_list = tkinter.Listbox(
            self._sidebar_bottom, selectmode=tkinter.MULTIPLE,
            bg="#555555", fg="#ffffff", relief=tkinter.FLAT, border="0"
        )
        self._answer_dict = dict()
        self._puzzle_origin = None
        self._puzzle_unit_x = None
        self._puzzle_unit_y = None
        self._answer_marking_dict = dict()

        # buttons
        self._open_button = customtkinter.CTkButton(
            self._sidebar, text='Open Image', command=self._open_image, font=self._font_button
        )
        self._reset_button = customtkinter.CTkButton(
            self._sidebar, text='Reset Solver', command=self._reset_app, font=self._font_button
        )
        self._process_button = customtkinter.CTkButton(
            self._sidebar, text='Solve', command=self._solve_puzzle, font=self._font_button
        )
        self._puzzle_select_button = customtkinter.CTkButton(
            self._sidebar, text='Select Word Search', command=self._begin_wordsearch_select, font=self._font_button
        )
        self._word_bank_select_button = customtkinter.CTkButton(
            self._sidebar, text='Select Word Bank', command=self._begin_wordbank_select, font=self._font_button
        )
        self._redo_select_button = customtkinter.CTkButton(
            self._sidebar_bottom, text='Redo Selection', command=self._reset_select, font=self._font_button
        )
        self._confirm_wordsearch_button = customtkinter.CTkButton(
            self._sidebar_bottom, text='Confirm Selection', command=self._confirm_wordsearch_selection, font=self._font_button
        )
        self._confirm_wordbank_button = customtkinter.CTkButton(
            self._sidebar_bottom, text='Confirm Selection', command=self._confirm_wordbank_selection, font=self._font_button
        )
        self._edit_wordsearch_form = customtkinter.CTkTextbox(
            self._sidebar_right_1, width=200, height=300, font=self._font_mono
        )
        self._edit_wordbank_form = customtkinter.CTkTextbox(
            self._sidebar_right_2, width=200, height=300, font=self._font_mono
        )
        self._confirm_edit_wordsearch_button = customtkinter.CTkButton(
            self._sidebar_right_bottom, text='Update Changes', command=self._update_wordsearch
        )

        # initialize positions
        # self._menu.grid(
        #     row=1, column=0, sticky= tkinter.S
        # )
        self._welcome_image_label.grid(
            row=0, column=1, rowspan=2,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W,
            padx=20
        )
        self._sidebar.grid(
            row=0, column=2, padx=5
        )
        self._sidebar_right_1.grid(
            row=0, column=3, sticky='S', padx=5
        )
        self._sidebar_right_2.grid(
            row=0, column=4, sticky='S', padx=5
        )

        self._open_button.grid(
            row=1, column=0, sticky='nesw', pady=5
        )
        # self._autosolve_mode.grid(
        #     row=0, column=0, sticky='n'
        # )
        self._reset_button.grid(
            row=0, column=0, sticky='nesw', pady=5
        )
        self._edit_wordsearch_form.grid(
            row=1, column=0
        )
        self._edit_wordbank_form.grid(
            row=1, column=0
        )

        # add labels
        customtkinter.CTkLabel(self._menu, text='Word Search Solver v2.0.1').pack()
        customtkinter.CTkLabel(self._menu, text='Created by Sean Collan Fong').pack()
        customtkinter.CTkLabel(self._sidebar_right_1, text='Word Search Text').grid(row=0, column=0)
        customtkinter.CTkLabel(self._sidebar_right_2, text='Word Bank Text').grid(row=0, column=0)
        self._word_select_list_label = customtkinter.CTkLabel(self._sidebar_bottom, text='Select words to solve:', padx=10, pady=5)
        self._select_wordsearch_label = customtkinter.CTkLabel(self._sidebar_bottom, text='Select the puzzle area.')
        self._select_wordbank_label = customtkinter.CTkLabel(self._sidebar_bottom, text='Select the wordbank area.')

    def _reset_app(self) -> None:
        '''
        Resets the application to its original state.
        '''
        # remove buttons
        self._puzzle_select_button.grid_forget()
        self._word_bank_select_button.grid_forget()
        self._process_button.grid_forget()
        self._redo_select_button.grid_forget()
        self._confirm_wordsearch_button.grid_forget()
        self._select_wordsearch_label.grid_forget()
        self._word_select_list_label.grid_forget()
        self._confirm_edit_wordsearch_button.grid_forget()
        self._edit_wordsearch_form.delete('1.0', tkinter.END)
        self._edit_wordbank_form.delete('1.0', tkinter.END)
        self._word_select_list.delete(0, tkinter.END)
        self._word_select_list.grid_forget()
        self._sidebar_bottom.grid_forget()
        self._sidebar_right_bottom.grid_forget()

        # add buttons
        self._open_button.grid(
            row=1, column=0, sticky='nesw'
        )

        # reset attributes
        self._puzzle_select_button.configure(state="normal")
        self._word_bank_select_button.configure(state="normal")
        self._reset_select()
        self._end_selection()
        self._bounding_box = None
        self._image_object = None
        self._wordsearch_info = None
        self._wordsearch_content = []
        self._wordbank_content = []
        self._wordbank_info = None
        self._wordsearch_results = None
        self._wordbank_results = None
        self._wordsearch_on_img = None
        self._wordbank_on_img = None
        self._answer_dict = dict()
        self._puzzle_origin = None
        self._puzzle_unit_x = None
        self._puzzle_unit_y = None
        self._answer_marking_dict = dict()

        self._canvas.grid_forget()
        self._welcome_image_label.grid(
            row=0, column=1, rowspan=2,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W,
            padx=20
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
        self._sidebar_bottom.grid(
            row=1, column=2
        )
        self._sidebar_right_bottom.grid(
            row=1, column=3, columnspan=2, sticky='N', pady=5
        )
        self._open_button.grid_forget()
        self._puzzle_select_button.grid(
            row=1, column=0, sticky='nesw', pady=5
        )
        self._word_bank_select_button.grid(
            row=2, column=0, sticky='nesw', pady=5
        )
        self._welcome_image_label.grid_forget()
        self._canvas.grid(
            row=0, column=1, rowspan=2,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W,
            padx=20, pady=10
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
            row=1, column=0, sticky='nesw', pady=5
        )
        self._confirm_wordbank_button.grid_forget()
        self._confirm_wordsearch_button.grid(
            row=2, column=0, sticky='nesw', pady=5
        )
        # edit labels
        self._select_wordbank_label.grid_forget()
        self._select_wordsearch_label.grid(
            row=0, column=0, pady=5
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
        self._puzzle_select_button.configure(state="disabled")
        self._redo_select_button.grid_forget()
        self._confirm_wordsearch_button.grid_forget()
        self._select_wordsearch_label.grid_forget()
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
            row=1, column=0, sticky='nesw', pady=5
        )
        self._confirm_wordsearch_button.grid_forget()
        self._confirm_wordbank_button.grid(
            row=2, column=0, sticky='nesw', pady=5
        )
        # edit labels
        self._select_wordsearch_label.grid_forget()
        self._select_wordbank_label.grid(
            row=0, column=0, pady=5
        )

    def _confirm_wordbank_selection(self) -> None:
        '''
        Confirms the word bank is selected
        '''
        self._end_selection()
        # remove selection buttons
        self._word_bank_select_button.configure(state="disabled")
        self._redo_select_button.grid_forget()
        self._confirm_wordbank_button.grid_forget()
        self._select_wordbank_label.grid_forget()
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
                row=3, column=0, pady=5
            )

    def _solve_puzzle(self) -> None:
        '''
        Solves the puzzle with all the data from image scanned
        '''
        # remove buttons
        self._process_button.grid_forget()
        self._word_bank_select_button.grid_forget()
        self._puzzle_select_button.grid_forget()
        self._open_button.grid_forget()

        # wordsearch section
        x1, y1 = self._wordsearch_info.get_x(), self._wordsearch_info.get_y()
        x2, y2 = self._wordsearch_info.get_end_x(), self._wordsearch_info.get_end_y()
        # print(x1, y1, x2, y2)
        self._wordsearch_results = self._image_object.process_selection(
            self.canvas_to_img(x1, y1), self.canvas_to_img(x2, y2),
            config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ1')

        # wordbank section
        x1, y1 = self._wordbank_info.get_x(), self._wordbank_info.get_y()
        x2, y2 = self._wordbank_info.get_end_x(), self._wordbank_info.get_end_y()
        # print(x1, y1, x2, y2)
        self._wordbank_results = self._image_object.process_selection(
            self.canvas_to_img(x1, y1), self.canvas_to_img(x2, y2),
            config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1')

        self.create_solution()

        # insert widgets
        self._word_select_list_label.grid(
            row=0, column=0
        )
        self._word_select_list.grid(
            row=1, column=0
        )



    def create_solution(self) -> None:
        '''
        Creates solution for puzzle after reading data
        '''
        # create a 2-D list with the current data
        self._wordsearch_content = []

        for ind, result in enumerate(self._wordsearch_results):
            line_as_char = []
            for char in result.char:
                line_as_char.append(char if char != '1' else 'I')
            self._wordsearch_content.append(line_as_char)

        self._calculate_units()
        # print(self._wordsearch_content)
        # update wordbank content
        self._wordbank_content = [entry.char for entry in self._wordbank_results]

        self.solve_and_update()

    def _calculate_units(self) -> None:
        '''
        Calculates units for drawing on canvas
        '''
        sum_height = self._wordsearch_results[-1].y + self._wordsearch_results[-1].h - self._wordsearch_results[0].y
        _, self._puzzle_unit_y = self.img_to_canvas(0, sum_height / len(self._wordsearch_content), rounding=False)
        self._puzzle_unit_x = self._puzzle_unit_y
        # print('units', self._puzzle_unit_x, self._puzzle_unit_y)

    def solve_and_update(self) -> None:
        '''
        Solves the puzzle and updates the answer dictionary
        '''
        # solve the wordsearch
        searcher = search.Searcher(self._wordsearch_content)

        self._word_select_list.delete(0, tkinter.END)

        print('Updating answers')
        # insert words into word list
        for index, result in enumerate(self._wordbank_content):
            word = result.upper()
            self._word_select_list.insert(index, word)
            self._answer_dict[word] = searcher.search(word)
        # print(self._answer_dict)
        self._word_select_list.bind('<<ListboxSelect>>', _word_selector(self))

        # show results and create update button
        self._confirm_edit_wordsearch_button.grid(
            row=0, column=0, sticky=tkinter.N, pady=5
        )

        for line_list in self._wordsearch_content:
            self._edit_wordsearch_form.insert('end', ''.join(line_list) + '\n')

        for line_list in self._wordbank_content:
            self._edit_wordbank_form.insert('end', ''.join(line_list) + '\n')

    def draw_solution(self, word) -> None:
        '''
        Draws a solution for the given word
        '''
        # update puzzle units
        self._create_puzzle_origin()
        origin_x, origin_y = self._puzzle_origin[0], self._puzzle_origin[1]
        found_search_list = self._answer_dict[word]
        for fs in found_search_list:
            # print(fs.r, fs.c)
            x1, y1 = origin_x + (self._puzzle_unit_x * fs.c), origin_y + (self._puzzle_unit_y * fs.r)
            x2, y2 = x1 + (fs.dx * (len(word) - 0.5) * self._puzzle_unit_x), y1 + \
                     (fs.dy * (len(word) - 0.5) * self._puzzle_unit_y)
            self._canvas.create_line(
                x1, y1, x2, y2,
                tags='solution-line', fill='green', stipple='gray50', width=8)

    def _create_puzzle_origin(self) -> None:
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
        # print('origin', self._puzzle_origin)

    def _update_wordsearch(self) -> None:
        '''
        Updates the puzzle after user edits its contents
        '''
        wordsearch_content = self._edit_wordsearch_form.get('1.0', 'end-1c')
        new_wordsearch_content = [list(line) for line in wordsearch_content.splitlines()]
        wordbank_content = self._edit_wordbank_form.get('1.0', 'end-1c')
        new_wordbank_content = [line for line in wordbank_content.splitlines()]
        self._edit_wordsearch_form.delete('1.0', tkinter.END)
        self._edit_wordbank_form.delete('1.0', tkinter.END)
        self._wordsearch_content = new_wordsearch_content
        self._wordbank_content = new_wordbank_content
        # print(self._wordbank_content)
        self.solve_and_update()
        self._calculate_units()
        # print(new_wordsearch_content)

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
            # print(self._bounding_box.get_x(), self._bounding_box.get_y(), event.x, event.y)
            print('Finished selecting bounding box')

    return _finish_draw


def image_updater(self, convert=False) -> callable:
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
        self._calculate_units()
        self._canvas.delete('solution-line')
        # print(selections)
        for index in selections:
            selection_name = event.widget.get(index)  # returns the indices selected in the listbox
            # solve this data
            # print(self._answer_dict[selection_name])
            try:
                self.draw_solution(selection_name)
            except Exception as e:
                print(e)
                print('Failed to draw solution')

    return _select


if __name__ == '__main__':
    SolverApp().run()
