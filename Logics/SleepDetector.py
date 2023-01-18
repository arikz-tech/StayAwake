import time


class SleepDetector:
    """
    Sleep Detector Class
    """

    def __init__(self):
        """
        Sleep Detector constructor
        """
        self.closed_eye = False
        self.is_sleeping = False
        self.ear_threshold = 0.19
        self.closed_eye_time = 0
        self.closed_eye_duration = 0

    def closed_eye_detection(self, ear):
        """
        Description: Detect if the eye closed for 1 second in order to recognize sleep
        :param ear:
        :return:
        """

        if ear > self.ear_threshold:
            self.is_sleeping = False
            self.closed_eye = False

        if ear <= self.ear_threshold and self.closed_eye is not True:
            self.closed_eye = True
            self.closed_eye_time = time.time()

        if self.closed_eye is True and self.is_sleeping is not True:
            keeping_eye_closed_time = time.time()
            eye_closed_duration = keeping_eye_closed_time - self.closed_eye_time

            if eye_closed_duration > 0.8:
                self.is_sleeping = True


    def falling_head_detection(self,angle_x, angle_y, angle_z):
        """
        Description: Detect if the head fall in order to recognize sleep
        :param angle_x:
        :param angle_y:
        :param angle_z:
        :return:
        """

        if angle_x > 12:
            self.is_sleeping = True

        if angle_z > 20:
            self.is_sleeping = True

        if angle_z < -20:
            self.is_sleeping = True
