from tkinter import *
from tkinter import ttk

raspberry_pi_resolution = "500x700"
background_color = "#00171F"

class StayAwakeUI:

    def __init__(self):
        self.root = Tk()
        self.root.geometry(raspberry_pi_resolution)
        self.root.configure(bg=background_color)
        self.root.title("StayAwake")
        Label(self.root, text="StayAwake System", font=("times new roman", 30, "bold"), bg=background_color,
              fg="white").pack()

        self.fatigue_description_label = Label(self.root, text="Hello man you are tired, please take a rest immediately", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.fatigue_description_label.pack()
        self.fatigue_description_label.place(relx=0.5, rely=0.8, anchor='center')

        self.label_frame = LabelFrame(self.root)
        self.label_frame.pack()
        self.label_frame.place(relx=0.5, rely=0.4, anchor='center')

        self.fatigue_level_label = Label(self.root, text="Fatigue Level", font=("times new roman", 15, "bold"),
                                    bg=background_color, fg="white")
        self.fatigue_level_label.pack()
        self.fatigue_level_label.place(relx=0.5, rely=0.9, anchor='center')

        self.face_angle_label = Label(self.root, text="", font=("times new roman", 15, "bold"),
                                         bg=background_color, fg="white")
        self.face_angle_label.pack()
        self.face_angle_label.place(relx=0.5, rely=0.65, anchor='center')

        self.blink_label = Label(self.root, text="Blinks", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.blink_label.pack()
        self.blink_label.place(relx=0.25, rely=0.14, anchor='center')

        self.snooze_label = Label(self.root, text="Snooze", font=("times new roman", 15, "bold"), bg=background_color, fg="white")
        self.snooze_label.pack()
        self.snooze_label.place(relx=0.5, rely=0.14, anchor='center')

        self.yawning_label = Label(self.root, text="Yawning", font=("times new roman", 15, "bold"), bg=background_color,
                              fg="white")
        self.yawning_label.pack()
        self.yawning_label.place(relx=0.75, rely=0.14, anchor='center')

        self.progress_bar = ttk.Progressbar(
            self.root,
            orient='horizontal',
            mode='determinate',
            length=350
        )
        self.progress_bar.pack()
        self.progress_bar.place(relx=0.5, rely=0.95, anchor='center')

        self.displayed_label_frame = Label(self.label_frame, width=350, height=350)
        self.displayed_label_frame.pack()