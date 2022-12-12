import winsound
import cv2
import dlib
from scipy.spatial import distance
from FatigueDetector import FatigueDetector
from SleepDetector import SleepDetector
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.geometry("800x540")
root.configure(bg="#00171F")
Label(root, text="StayAwake System", font=("times new roman", 30, "bold"), bg="#00171F", fg="white").pack()

blink_label = Label(root, text="Blinks", font=("times new roman", 15, "bold"), bg="#00171F", fg="white")
blink_label.pack()
blink_label.place(relx=0.35, rely=0.5, anchor='center')

snooze_label = Label(root, text="Snooze", font=("times new roman", 15, "bold"), bg="#00171F", fg="white")
snooze_label.pack()
snooze_label.place(relx=0.35, rely=0.55, anchor='center')

yawning_label = Label(root, text="Yawning", font=("times new roman", 15, "bold"), bg="#00171F", fg="white")
yawning_label.pack()
yawning_label.place(relx=0.35, rely=0.6, anchor='center')


label_frame = LabelFrame(root, bg="white")
label_frame.pack()
label_frame.place(relx=0.7, rely=0.6, anchor='center')

displayed_label_frame = Label(label_frame, bg="white", width=400, height=400)
displayed_label_frame.pack()
root.bind('<Escape>', lambda e: close_win(e))
cap = cv2.VideoCapture(0)


def close_win(e):
    root.destroy()
    cap.release()


class StayAwake:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    fatigue_detector = FatigueDetector()
    sleep_detector = SleepDetector()

    def run(self):
        while True:
            # Find haar cascade to draw bounding box around face
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = ImageTk.PhotoImage(Image.fromarray(frame))
            displayed_label_frame['image'] = image
            faces = self.detector(gray)
            if faces:
                for face in faces:
                    x1 = face.left()
                    y1 = face.top()
                    x2 = face.right()
                    y2 = face.bottom()
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    landmarks = self.predictor(gray, face)
                    left_eye = []
                    right_eye = []
                    mouth = []

                    # Making mouth points list
                    for i in range(60, 68):
                        mouth.append(landmarks.part(i))

                    # Making left eye and right eye points list
                    for i in range(6):
                        left_eye.append(landmarks.part(36 + i))
                        right_eye.append(landmarks.part(42 + i))

                    self._print_face_part(mouth, frame, (0, 255, 0))
                    self._print_face_part(left_eye, frame, (0, 255, 0))
                    self._print_face_part(right_eye, frame, (0, 255, 0))

                    average_ear = self._eye_average_aspect_ratio(left_eye, right_eye)
                    average_mar = self._mouth_aspect_ratio(mouth)

                    self.fatigue_detector.eyes_symptoms_classification(average_ear)
                    self.fatigue_detector.mouth_symptoms_classification(average_mar)

                    self.sleep_detector.closed_eye_detection(average_ear)

                    duration = 100  # milliseconds
                    freq = 400  # Hz

                    if self.sleep_detector.is_sleeping:
                        # print("Fall asleep")
                        winsound.Beep(freq, duration)

                    self.fatigue_detector.drowsiness_detection()

                    blink_label['text'] = f"Blinks:{self.fatigue_detector.blinks_per_minuets} "
                    snooze_label['text'] = f"Snoozes: :{self.fatigue_detector.number_of_snooze} "
                    yawning_label['text'] = f"yawing :{self.fatigue_detector.numbers_of_yaws} "

                    if self.fatigue_detector.drowsy_indicator > 10:
                        print("hello man you are tired")
            root.update()



    def _eye_aspect_ratio(self, eye_points):
        """
        :param eye_points:
        :return:
        """
        p1 = [eye_points[0].x, eye_points[0].y]
        p2 = [eye_points[1].x, eye_points[1].y]
        p3 = [eye_points[2].x, eye_points[2].y]
        p4 = [eye_points[3].x, eye_points[3].y]
        p5 = [eye_points[4].x, eye_points[4].y]
        p6 = [eye_points[5].x, eye_points[5].y]
        AL = distance.euclidean(p2, p6)
        BL = distance.euclidean(p3, p5)
        CL = distance.euclidean(p1, p4)
        EAR = (AL + BL) / (2 * CL)
        return EAR

    def _mouth_aspect_ratio(self, mouth_points):
        """

        :param mouth_points:
        :return: the aspect ratio of the mouth
        """
        p7 = [mouth_points[0].x, mouth_points[0].y]
        p8 = [mouth_points[1].x, mouth_points[1].y]
        p9 = [mouth_points[2].x, mouth_points[2].y]
        p10 = [mouth_points[3].x, mouth_points[3].y]
        p11 = [mouth_points[4].x, mouth_points[4].y]
        p12 = [mouth_points[5].x, mouth_points[5].y]
        p13 = [mouth_points[6].x, mouth_points[6].y]
        p14 = [mouth_points[7].x, mouth_points[7].y]

        # the mar that calculated from the out-lips points
        mar = (distance.euclidean(p14, p8) + distance.euclidean(p13, p9) + distance.euclidean(p12, p10)) / (3 * (
            distance.euclidean(p11, p7)))

        return mar

    def _eye_average_aspect_ratio(self, left_eye, right_eye):
        # Calculate left eye aspect ratio and right eye aspect ratio, in order to determine if the eye is open or closed
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)

        # Average eye aspect ratio of both eyes
        avg_ear = (left_ear + right_ear) / 2

        return avg_ear

    def _print_face_part(self, part, frame, color):
        for dot in part:
            x = dot.x
            y = dot.y
            cv2.circle(frame, (x, y), 1, color, -1)
