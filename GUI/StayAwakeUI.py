from tkinter import *
from tkinter import ttk

raspberry_pi_resolution = "500x700"
background_color = "#00171F"


class StayAwakeUI:

    def __init__(self):
        """
        StayAwake User interface constructor
        """
        self.root = Tk()
        self.root.geometry(raspberry_pi_resolution)
        self.root.configure(bg=background_color)
        self.root.title("StayAwake")
        Label(self.root, text="StayAwake System", font=("times new roman", 30, "bold"), bg=background_color,
              fg="white").pack()

        self.progress_bar = self._create_progres_bar()
        self.displayed_label_frame = self._create_frame_windows()

        self.fatigue_description_label = self._create_label(text="", x_pos=0.5, y_pos=0.8, color="white",
                                                            background_color=background_color)
        self.fatigue_level_label = self._create_label(text="Fatigue level", x_pos=0.5, y_pos=0.9, color="white",
                                                      background_color=background_color)
        self.face_angle_label = self._create_label(text="", x_pos=0.5, y_pos=0.65, color="white",
                                                   background_color=background_color)
        self.blink_label = self._create_label(text="Blinks", x_pos=0.25, y_pos=0.14, color="white",
                                              background_color=background_color)
        self.snooze_label = self._create_label(text="Snooze", x_pos=0.5, y_pos=0.14, color="white",
                                               background_color=background_color)
        self.yawning_label = self._create_label(text="Yawing", x_pos=0.75, y_pos=0.14, color="white",
                                                background_color=background_color)


    def _create_frame_windows(self):
        frame_widnows = LabelFrame(self.root)
        frame_widnows.pack()
        frame_widnows.place(relx=0.5, rely=0.4, anchor='center')
        display_windows = Label(frame_widnows, width=350, height=350)
        display_windows.pack()
        return display_windows

    def _create_label(self, text, x_pos, y_pos, color, background_color):
        """

        :param text:
        :param x_pos:
        :param y_pos:
        :param color:
        :return:
        """
        label = Label(self.root, text=text, font=("times new roman", 15, "bold"), bg=background_color,
                      fg=color)
        label.pack()
        label.place(relx=x_pos, rely=y_pos, anchor='center')
        return label

    def _create_progres_bar(self):
        progress_bar = ttk.Progressbar(
            self.root,
            orient='horizontal',
            mode='determinate',
            length=350
        )
        progress_bar.pack()
        progress_bar.place(relx=0.5, rely=0.95, anchor='center')
        return progress_bar
