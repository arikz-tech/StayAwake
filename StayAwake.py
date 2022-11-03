import cv2
import dlib


class StayAwake:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
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
                    for i in range(0, 67):
                        x = landmarks.part(i).x
                        y = landmarks.part(i).y
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        print("dvir")
