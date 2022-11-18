import cv2
import dlib
import matplotlib.pyplot as plt
import time

from FatigueDetector import FatigueDetector
from SleepDetector import SleepDetector


class StayAwake:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    fatigue_detector = FatigueDetector()
    sleep_detector = SleepDetector()

    cap = cv2.VideoCapture(0)

    def run(self):
        EAR = [0]
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

                    # Making left eye and right eye list
                    for i in range(6):
                        left_eye.append(landmarks.part(36 + i))
                        right_eye.append(landmarks.part(42 + i))

                    # Print to frame left eye and right eye
                    for i in range(36, 48):
                        x = landmarks.part(i).x
                        y = landmarks.part(i).y
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

                    EAR.append(self.fatigue_detector.blink_detection(left_eye, right_eye))
                    cv2.putText(frame, f"EAR:{EAR[-1]} ", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, f"Blinks:{self.fatigue_detector.blinks_per_minuets} ", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print(EAR)
        close_eye = False
        blink = 0
        for i in range(0, len(EAR) - 1):
            if EAR[i] < 0.2:
                if EAR[i + 1] > 0.2 or EAR[i + 2] > 0.2 or EAR[i + 3] > 0.2:
                    blink = blink + 1

        plt.plot(EAR)
        print(blink)
        # naming the x axis
        plt.xlabel('x - axis')
        # naming the y axis
        plt.ylabel('y - axis')

        # function to show the plot
        plt.show()
        self.cap.release()
        new_frame_time = time.time()

        # Calculating the fps

        cv2.destroyAllWindows()
