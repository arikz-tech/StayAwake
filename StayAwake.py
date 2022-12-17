import winsound
import cv2
import dlib
from scipy.spatial import distance
from FatigueDetector import FatigueDetector
from SleepDetector import SleepDetector
from PIL import Image, ImageTk
from StayAwakeUI import StayAwakeUI

class StayAwake:

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.fatigue_detector = FatigueDetector()
        self.sleep_detector = SleepDetector()
        self.app = StayAwakeUI()
        self.cap = cv2.VideoCapture(0)
        self.app.root.bind('<Escape>', lambda e: self.close_win(e))

    def run(self):
        while True:
            # Find haar cascade to draw bounding box around face
            ret, frame = self.cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.detector(gray)
            if faces:
                for face in faces:
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

                    self._add_face_part_dots(mouth, frame, (0, 255, 0))
                    self._add_face_part_dots(left_eye, frame, (0, 255, 0))
                    self._add_face_part_dots(right_eye, frame, (0, 255, 0))

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

                    self.app.blink_label['text'] = f"Blinks:{self.fatigue_detector.blinks_per_minuets} "
                    self.app.snooze_label['text'] = f"Snoozes: :{self.fatigue_detector.number_of_snooze} "
                    self.app.yawning_label['text'] = f"yawing :{self.fatigue_detector.numbers_of_yaws} "

                    if self.fatigue_detector.drowsy_indicator > 10:
                        print("hello man you are tired")

            # display the frame on the tkinter GUI
            blue, green, red = cv2.split(frame)
            img = cv2.merge((red, green, blue))
            im = Image.fromarray(img)
            image = ImageTk.PhotoImage(image=im)
            self.app.displayed_label_frame['image'] = image
            self.app.root.update()

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

    def _add_face_part_dots(self, part, frame, color):
        for dot in part:
            x = dot.x
            y = dot.y
            cv2.circle(frame, (x, y), 1, color, -1)

    def close_win(self, e):
        self.app.root.destroy()
        self.cap.release()