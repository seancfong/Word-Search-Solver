'''
The interface.py module implements functionality for creating
a user interface to import and view solvable puzzles
'''

import tkinter

class SolverApp:
    def __init__(self):
        self._root_window = tkinter.Tk()

    def _refresh_display(self):
        '''
        Refreshes the display
        '''
        pass

    def run(self):
        '''
        Runs the main loop
        '''
        self._refresh_display()
        self._root_window.mainloop()


if __name__ == '__main__':
    SolverApp().run()