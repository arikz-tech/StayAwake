from scipy.spatial import distance
import time


class FatigueDetector:
    blinks_per_minuets = 0
    numbers_of_yaws = 0
    number_of_snooze = 0
    ear_threshold = 0.2
    closed_eye = False
    open_eye = False
    close_eye_time = 0
    open_eye_time = 0
    blink_duration_time = 0

    def blink_detection(self, left_eye: list, right_eye: list):
        """

        :return:
        """
        left_ear = self._eye_aspect_ratio_calculate(left_eye)
        right_ear = self._eye_aspect_ratio_calculate(right_eye)
        avg_ear = (left_ear + right_ear) / 2

        if avg_ear <= self.ear_threshold and self.closed_eye is not True:
            self.open_eye = False
            self.closed_eye = True
            self.close_eye_time = time.time()

        if avg_ear > self.ear_threshold and self.open_eye is not True:
            self.open_eye = True
            self.closed_eye = False
            self.open_eye_time = time.time()

            self.blink_duration_time = self.open_eye_time - self.close_eye_time

            if 0.05 < self.blink_duration_time < 0.15:
                self.blinks_per_minuets = self.blinks_per_minuets + 1

        return avg_ear

    def _eye_aspect_ratio_calculate(self, eye: list):
        """

        :param eye:
        :return:
        """
        p1 = [eye[0].x, eye[0].y]
        p2 = [eye[1].x, eye[1].y]
        p3 = [eye[2].x, eye[2].y]
        p4 = [eye[3].x, eye[3].y]
        p5 = [eye[4].x, eye[4].y]
        p6 = [eye[5].x, eye[5].y]
        AL = distance.euclidean(p2, p6)
        BL = distance.euclidean(p3, p5)
        CL = distance.euclidean(p1, p4)
        EAR = (AL + BL) / (2 * CL)
        return EAR

    def yawning_detection(self, mouth):
        """

        :return:
        """

    def snooze_detection(self, left_eye, right_eye):
        """

        :return:
        """
