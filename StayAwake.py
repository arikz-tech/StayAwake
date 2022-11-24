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

                    # Making left eye and right eye list
                    for i in range(48, 60):
                        mouth.append(landmarks.part(i))

                    # Making left eye and right eye list
                    for i in range(6):
                        left_eye.append(landmarks.part(36 + i))
                        right_eye.append(landmarks.part(42 + i))

                    self.printFacePart(mouth, frame, (0, 0, 255))
                    self.printFacePart(left_eye, frame, (0, 255, 0))
                    self.printFacePart(right_eye, frame, (0, 255, 0))

                    average_ear = self._eye_average_aspect_ratio(left_eye, right_eye)

                    # mar = self.mouth_aspect_ratio(mouth)
                    self.fatigue_detector.eyes_symptoms_classification(average_ear)
                    self.sleep_detector.closed_eye_detection(average_ear)

                    duration = 100  # milliseconds
                    freq = 400  # Hz

                    if self.sleep_detector.is_sleeping:
                        winsound.Beep(freq, duration)

                    self.fatigue_detector.drowsiness_detection()

                    cv2.putText(frame, f"Blinks:{self.fatigue_detector.blinks_per_minuets} ", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, f"Snoozes: :{self.fatigue_detector.number_of_snooze} ", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, f"Sleeping :{self.sleep_detector.is_sleeping} ", (50, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

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

    def _eye_average_aspect_ratio(self, left_eye, right_eye):
        # Calculate left eye aspect ratio and right eye aspect ratio, in order to determine if the eye is open or closed
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)

        # Average eye aspect ratio of both eyes
        avg_ear = (left_ear + right_ear) / 2

        return avg_ear

    def mouth_aspect_ratio(self, mouth):
        pass

    def printFacePart(self, part, frame, color):
        for dot in part:
            x = dot.x
            y = dot.y
            cv2.circle(frame, (x, y), 1, color, -1)
