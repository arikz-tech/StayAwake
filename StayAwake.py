import winsound
import cv2
import dlib
from scipy.spatial import distance
from FatigueDetector import FatigueDetector
from SleepDetector import SleepDetector
from PIL import Image, ImageTk
from StayAwakeUI import StayAwakeUI
from imutils import face_utils
import numpy as np

import pyttsx3
import threading


K = [6.5308391993466671e+002, 0.0, 3.1950000000000000e+002,
     0.0, 6.5308391993466671e+002, 2.3950000000000000e+002,
     0.0, 0.0, 1.0]
D = [7.0834633684407095e-002, 6.9140193737175351e-002, 0.0, 0.0, -1.3073460323689292e+000]

cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)

object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                         [1.330353, 7.122144, 6.903745],
                         [-1.330353, 7.122144, 6.903745],
                         [-6.825897, 6.760612, 4.402142],
                         [5.311432, 5.485328, 3.987654],
                         [1.789930, 5.393625, 4.413414],
                         [-1.789930, 5.393625, 4.413414],
                         [-5.311432, 5.485328, 3.987654],
                         [2.005628, 1.409845, 6.165652],
                         [-2.005628, 1.409845, 6.165652],
                         [2.774015, -2.080775, 5.048531],
                         [-2.774015, -2.080775, 5.048531],
                         [0.000000, -3.116408, 6.097667],
                         [0.000000, -7.415691, 4.070434]])

reprojectsrc = np.float32([[10.0, 10.0, 10.0],
                           [10.0, 10.0, -10.0],
                           [10.0, -10.0, -10.0],
                           [10.0, -10.0, 10.0],
                           [-10.0, 10.0, 10.0],
                           [-10.0, 10.0, -10.0],
                           [-10.0, -10.0, -10.0],
                           [-10.0, -10.0, 10.0]])

line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
              [4, 5], [5, 6], [6, 7], [7, 4],
              [0, 4], [1, 5], [2, 6], [3, 7]]


class StayAwake:

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.fatigue_detector = FatigueDetector()
        self.sleep_detector = SleepDetector()
        self.app = StayAwakeUI()
        self.cap = cv2.VideoCapture(0)
        self.app.root.bind('<Escape>', lambda e: self.close_win(e))
        self.engine = pyttsx3.init()

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

                    shape = face_utils.shape_to_np(landmarks)

                    reprojectdst, euler_angle = self.get_head_pose(shape)
                    angele_x = euler_angle[0, 0]
                    angele_y = euler_angle[1, 0]
                    angele_z = euler_angle[2, 0]

                    self.app.fatigue_description_label['text'] = "X: " + "{:7.2f}".format(angele_x) + " Y: " + "{:7.2f}".format(angele_y) + " Z: " + "{:7.2f}".format(angele_z)
                    duration = 100  # milliseconds
                    freq = 400  # Hz

                    # if self.sleep_detector.is_sleeping:
                    #     # print("Fall asleep")
                    #     winsound.Beep(freq, duration)

                    self.fatigue_detector.drowsiness_detection()

                    self.app.progress_bar['value'] = (self.fatigue_detector.drowsy_level / 5) * 100

                    if self.fatigue_detector.drowsy_level == 1 and self.fatigue_detector.start_voice_flag:
                        fatigue_text = "Hey, you seem to be a little tired, please take a break"
                        self.app.fatigue_description_label['text'] = fatigue_text
                        self.text_to_voice(fatigue_text)

                    elif self.fatigue_detector.drowsy_level == 2 and self.fatigue_detector.start_voice_flag:
                        fatigue_text = "Hey,again Fuck You Wake Up !!!!!!!"
                        self.app.fatigue_description_label['text'] = fatigue_text
                        self.text_to_voice(fatigue_text)

                    elif self.fatigue_detector.drowsy_level == 3 and self.fatigue_detector.start_voice_flag:
                        fatigue_text = ""
                        self.app.fatigue_description_label['text'] = fatigue_text
                        self.text_to_voice(fatigue_text)

                    elif self.fatigue_detector.drowsy_level == 4 and self.fatigue_detector.start_voice_flag:
                        fatigue_text = ""
                        self.app.fatigue_description_label['text'] = fatigue_text
                        self.text_to_voice(fatigue_text)

                    elif self.fatigue_detector.drowsy_level == 5 and self.fatigue_detector.start_voice_flag:
                        fatigue_text = ""
                        self.app.fatigue_description_label['text'] = fatigue_text
                        self.text_to_voice(fatigue_text)

                    self.fatigue_detector.start_voice_flag = False
                    self.app.blink_label['text'] = f"Blinks:{self.fatigue_detector.blinks_per_minuets} "
                    self.app.snooze_label['text'] = f"Snoozes: :{self.fatigue_detector.number_of_snooze} "
                    self.app.yawning_label['text'] = f"yawing :{self.fatigue_detector.numbers_of_yaws} "

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

    def text_to_voice(self, text):
        threading.Thread(
            target=self.run_pyttsx3, args=(text,), daemon=True
        ).start()

    def run_pyttsx3(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def get_head_pose(self, shape):
        image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                                shape[39], shape[42], shape[45], shape[31], shape[35],
                                shape[48], shape[54], shape[57], shape[8]])

        _, rotation_vec, translation_vec = cv2.solvePnP(object_pts, image_pts, cam_matrix, dist_coeffs)

        reprojectdst, _ = cv2.projectPoints(reprojectsrc, rotation_vec, translation_vec, cam_matrix,
                                            dist_coeffs)

        reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))

        # calc euler angle
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

        return reprojectdst, euler_angle