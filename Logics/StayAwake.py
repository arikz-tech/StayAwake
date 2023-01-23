import winsound
import cv2
import dlib
from scipy.spatial import distance
from Logics.FatigueDetector import FatigueDetector
from Logics.SleepDetector import SleepDetector
from Logics.stayawake_matrices import Matrices
from PIL import Image, ImageTk
from GUI.StayAwakeUI import StayAwakeUI
from imutils import face_utils
import numpy as np
from playsound import playsound
import time
import pyttsx3
import threading


class StayAwake:
    """
    StayAwake Class
    """

    def __init__(self):
        """
        StayAwake Class constructor
        """
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("Logics/shape_predictor_68_face_landmarks.dat")
        self.fatigue_detector = FatigueDetector()
        self.sleep_detector = SleepDetector()
        self.app = StayAwakeUI()
        self.cap = cv2.VideoCapture(0)
        self.app.root.bind('<Escape>', lambda e: self.close_win(e))
        self.engine = pyttsx3.init()
        self.sleeping_time = 0
        self.frame_count=0

    def run(self):
        """
        Description: Run StayAwake system
        :return:
        """
        while True:
            self.frame_count+=1
            # Find haar cascade to draw bounding box around face
            ret, frame = self.cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.detector(gray)
            if faces:
                driver_face = self.get_driver_face(faces, frame)
                landmarks = self.predictor(gray, driver_face)

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

                self.sleep_detector.falling_head_detection(angele_x, angele_y, angele_z)

                self.app.face_angle_label['text'] = "X: " + "{:7.2f}".format(
                    angele_x) + " Y: " + "{:7.2f}".format(angele_y) + " Z: " + "{:7.2f}".format(angele_z)

                self.fatigue_detector.drowsiness_detection()

                self.app.progress_bar['value'] = (self.fatigue_detector.drowsy_level / 5) * 100

                self.show_and_sound_fatigue_description()

                self.fatigue_detector.start_voice_flag = False
                self.app.blink_label['text'] = f"Blinks:{self.fatigue_detector.blinks_per_minuets} "
                self.app.snooze_label['text'] = f"Snoozes: :{self.fatigue_detector.number_of_snooze} "
                self.app.yawning_label['text'] = f"Yawing :{self.fatigue_detector.numbers_of_yaws} "
                curr_time = time.time()
                diff = curr_time - self.sleeping_time
                if self.sleep_detector.is_sleeping and diff > 10:
                    self.sleeping_time = time.time()
                    threading.Thread(
                        target=self.play_alram_sound, daemon=True
                    ).start()

            else:
                if self.frame_count>100:
                    print("no face")
                    threading.Thread(
                        target=self.play_alram_sound, daemon=True
                    ).start()
                    self.frame_count=0


            # display the frame on the tkinter GUI
            blue, green, red = cv2.split(frame)
            img = cv2.merge((red, green, blue))
            im = Image.fromarray(img)
            image = ImageTk.PhotoImage(image=im)
            self.app.displayed_label_frame['image'] = image
            self.app.root.update()

    def get_driver_face(self, faces, frame):
        """
        Description: get the main(driver face) face coordinate from the all the faces in the frame
        :param faces:
        :param frame:
        :return: Rectangle coordinates of the driver faces
        """
        max_per = 0
        driver_face = 0
        driver_frame = 0
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()
            width = x2 - x1
            height = y2 - y1
            perimeter = 2 * (width + height)
            if perimeter > max_per:
                max_per = perimeter
                driver_face = face
        return driver_face

    def show_and_sound_fatigue_description(self):
        """
        Description: Display and sound massage to the driver
        :return:
        """
        if self.fatigue_detector.drowsy_level == 1 and self.fatigue_detector.start_voice_flag:
            fatigue_text = "Hey, you seem to be a little tired, please take a break"
            self.app.fatigue_description_label['text'] = fatigue_text
            self.text_to_voice(fatigue_text)

        elif self.fatigue_detector.drowsy_level == 2 and self.fatigue_detector.start_voice_flag:
            fatigue_text = "Hey again, please take a break"
            self.app.fatigue_description_label['text'] = fatigue_text
            self.text_to_voice(fatigue_text)

        elif self.fatigue_detector.drowsy_level == 3 and self.fatigue_detector.start_voice_flag:
            fatigue_text = "Sorry to interrupt you but i think you should take a rest "
            self.app.fatigue_description_label['text'] = fatigue_text
            self.text_to_voice(fatigue_text)

        elif self.fatigue_detector.drowsy_level == 4 and self.fatigue_detector.start_voice_flag:
            fatigue_text = "Please take a break, The system detected that you are too tired to drive"
            self.app.fatigue_description_label['text'] = fatigue_text
            self.text_to_voice(fatigue_text)

        elif self.fatigue_detector.drowsy_level == 5 and self.fatigue_detector.start_voice_flag:
            fatigue_text = "Seriously, i suggest you to stop the car immediately you are tired!"
            self.app.fatigue_description_label['text'] = fatigue_text
            self.text_to_voice(fatigue_text)

    def _eye_aspect_ratio(self, eye_points):
        """
        Description: Calculate the eye aspect ratio
        :param eye_points:
        :return: Eye aspect ratio
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
        Description: Calculate the mouth aspect ratio
        :param mouth_points:
        :return: mouth aspect ratio
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
        """
        Description: Calculate the average Eyes aspect ratio
        :param left_eye:
        :param right_eye:
        :return: Average Eyes aspect ratio
        """
        # Calculate left eye aspect ratio and right eye aspect ratio, in order to determine if the eye is open or closed
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)

        # Average eye aspect ratio of both eyes
        avg_ear = (left_ear + right_ear) / 2

        return avg_ear

    def _add_face_part_dots(self, part, frame, color):
        """
        Description: Prints face part dots on the frame
        :param part:
        :param frame:
        :param color:
        :return:
        """
        for dot in part:
            x = dot.x
            y = dot.y
            cv2.circle(frame, (x, y), 2, color, -1)

    def close_win(self, e):
        """
        Description: Close the window and release the camera
        :param e:
        :return:
        """
        self.app.root.destroy()
        self.cap.release()

    def text_to_voice(self, text):
        """
        Description: Sound the input text as voice.
        :param text:
        :return:
        """
        threading.Thread(
            target=self.run_pyttsx3, args=(text,), daemon=True
        ).start()

    def play_alram_sound(self):
        """
        Description: Sound an alarm
        :return:
        """
        playsound('GUI/Sounds/sleep_alarm.wav')

    def run_pyttsx3(self, text):
        """

        :param text:
        :return:
        """
        self.engine.say(text)
        self.engine.runAndWait()

    def get_head_pose(self, shape):
        """
        Description: Finds the pose of the drivers head
        :param shape:
        :return: the Euler angles of the head pose
        """
        image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                                shape[39], shape[42], shape[45], shape[31], shape[35],
                                shape[48], shape[54], shape[57], shape[8]])

        _, rotation_vec, translation_vec = cv2.solvePnP(Matrices.object_pts, image_pts, Matrices.cam_matrix,
                                                        Matrices.dist_coeffs)

        reprojectdst, _ = cv2.projectPoints(Matrices.reprojectsrc, rotation_vec, translation_vec, Matrices.cam_matrix,
                                            Matrices.dist_coeffs)

        reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))

        # calc euler angle
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

        return reprojectdst, euler_angle
