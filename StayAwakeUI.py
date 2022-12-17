from tkinter import *
from tkinter import ttk

raspberry_pi_resolution = "800x480"
background_color = "#00171F"


class StayAwakeUI:

    def __init__(self):
        self.root = Tk()
        self.root.geometry(raspberry_pi_resolution)
        self.root.configure(bg=background_color)
        Label(self.root, text="StayAwake System", font=("times new roman", 30, "bold"), bg=background_color,
              fg="white").pack()

        self.blink_label = Label(self.root, text="Blinks", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.blink_label.pack()
        self.blink_label.place(relx=0.58, rely=0.2, anchor='center')

        self.snooze_label = Label(self.root, text="Snooze", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.snooze_label.pack()
        self.snooze_label.place(relx=0.75, rely=0.2, anchor='center')

        self.yawning_label = Label(self.root, text="Yawning", font=("times new roman", 15, "bold"), bg=background_color,
                              fg="white")
        self.yawning_label.pack()
        self.yawning_label.place(relx=0.925, rely=0.2, anchor='center')

        self.fatigue_description_label = Label(self.root, text="", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.fatigue_description_label.pack()
        self.fatigue_description_label.place(rely=0.4, anchor='w')

        self.label_frame = LabelFrame(self.root)
        self.label_frame.pack()
        self.label_frame.place(relx=0.75, rely=0.6, anchor='center')

        self.fatigue_level_label = Label(self.root, text="Fatigue Level", font=("times new roman", 15, "bold"),
                                    bg=background_color, fg="white")
        self.fatigue_level_label.pack()
        self.fatigue_level_label.place(relx=0.25, rely=0.89, anchor='center')

        self.progress_bar = ttk.Progressbar(
            self.root,
            orient='horizontal',
            mode='determinate',
            length=350
        )
        self.progress_bar.pack()
        self.progress_bar.place(relx=0.25, rely=0.95, anchor='center')

        self.displayed_label_frame = Label(self.label_frame, width=350, height=350)
        self.displayed_label_frame.pack()