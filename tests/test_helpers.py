"""Helper functions for testing tkinter without a display."""

import tkinter as tk


class DummyTk(tk.Tk):
    """A dummy Tk root that doesn't actually create a window."""

    def __init__(self):
        self.deiconify = lambda: None
        self.geometry = lambda x: None

    def withdraw(self):
        """Dummy withdraw method."""
        pass

    def destroy(self):
        """Dummy destroy method."""
        pass


def create_test_root():
    """Create a test root window that doesn't require a display."""
    try:
        root = tk.Tk()
        root.withdraw()
        return root
    except tk.TclError:
        return DummyTk()
