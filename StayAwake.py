import winsound
import cv2
import dlib
from scipy.spatial import distance
from FatigueDetector import FatigueDetector
from SleepDetector import SleepDetector


class StayAwake:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    fatigue_detector = FatigueDetector()
    sleep_detector = SleepDetector()

    cap = cv2.VideoCapture(0)

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
                    for i in range(48, 68):
                        mouth.append(landmarks.part(i))

                    # Making left eye and right eye points list
                    for i in range(6):
                        left_eye.append(landmarks.part(36 + i))
                        right_eye.append(landmarks.part(42 + i))

                    self._printFacePart(mouth, frame, (0, 0, 255))
                    self._printFacePart(left_eye, frame, (0, 255, 0))
                    self._printFacePart(right_eye, frame, (0, 255, 0))

                    average_ear = self._eye_average_aspect_ratio(left_eye, right_eye)

                    mar = self._mouth_aspect_ratio(mouth)
                    #print(mar)
                    self.fatigue_detector.eyes_symptoms_classification(average_ear)
                    self.sleep_detector.closed_eye_detection(average_ear)

                    duration = 100  # milliseconds
                    freq = 400  # Hz

                    if self.sleep_detector.is_sleeping:
                        #print("Fall asleep")
                        winsound.Beep(freq, duration)

                    self.fatigue_detector.drowsiness_detection()

                    cv2.putText(frame, f"Blinks:{self.fatigue_detector.blinks_per_minuets} ", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    cv2.putText(frame, f"Snoozes: :{self.fatigue_detector.number_of_snooze} ", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    cv2.putText(frame, f"Sleeping :{self.sleep_detector.is_sleeping} ", (50, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

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

        p15 = [mouth_points[8].x, mouth_points[8].y]
        p16 = [mouth_points[9].x, mouth_points[9].y]
        p17 = [mouth_points[10].x, mouth_points[10].y]
        p18 = [mouth_points[11].x, mouth_points[11].y]
        p19 = [mouth_points[12].x, mouth_points[12].y]
        p20 = [mouth_points[13].x, mouth_points[13].y]
        p21 = [mouth_points[14].x, mouth_points[14].y]
        p22 = [mouth_points[15].x, mouth_points[15].y]

        # the mar that calculated from the out-lips points
        outside_mar = (distance.euclidean(p14, p8) + distance.euclidean(p13, p9) + distance.euclidean(p12, p10)) / 3 * (
            distance.euclidean(p11, p7))

        # the mar that calculated from the in-lips points
        inside_mar = (distance.euclidean(p22, p16) + distance.euclidean(p21, p17) + distance.euclidean(p20, p18)) / (
                3 * distance.euclidean(p19, p15))

        avg_mar = inside_mar + outside_mar / 2
        return avg_mar

    def _eye_average_aspect_ratio(self, left_eye, right_eye):
        # Calculate left eye aspect ratio and right eye aspect ratio, in order to determine if the eye is open or closed
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)

        # Average eye aspect ratio of both eyes
        avg_ear = (left_ear + right_ear) / 2

        return avg_ear

    def _printFacePart(self, part, frame, color):
        for dot in part:
            x = dot.x
            y = dot.y
            cv2.circle(frame, (x, y), 1, color, -1)
