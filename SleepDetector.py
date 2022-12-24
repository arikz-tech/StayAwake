import time


class SleepDetector:
    closed_eye = False
    is_sleeping = False
    ear_threshold = 0.19
    closed_eye_time = 0
    closed_eye_duration = 0

    def closed_eye_detection(self, ear):
        """
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

            if eye_closed_duration > 1:
                self.is_sleeping = True


    def falling_head_detection(self,angle_x, angle_y, angle_z):
        """

        :return:
        """
        if angle_x > 12:
            self.is_sleeping = True

        if angle_z > 20:
            self.is_sleeping = True

        if angle_z < -20:
            self.is_sleeping = True
