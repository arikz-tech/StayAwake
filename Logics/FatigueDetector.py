import time


class FatigueDetector:

    def __init__(self):
        """
        FatigueDetector constructor
        """
        self.blinks_per_minuets = 0
        self.numbers_of_yaws = 0
        self.number_of_snooze = 0
        self.time_window_seconds = 0
        self.time_window_minutes = 0
        self.starting_time_window = 0
        self.drowsy_indicator = 0
        self.ear_threshold = 0.18
        self.mar_threshold = 0.2
        self.closed_eye = False
        self.open_mouth = False
        self.isDrowsy = False
        self.close_eye_time = 0
        self.open_eye_time = 0
        self.close_mouth_time = 0
        self.open_mouth_time = 0
        self.blinking_hazard = 0
        self.drowsy_level = 0  # 1-5
        self.start_voice_flag = False

    def eyes_symptoms_classification(self, ear):
        """
        Description: Classification of eye symptoms using the Eye aspect ratio and  closed eye duration
        :param ear:
        :return:
        """

        # Check whether the eye closed (ear < ear_threshold), when the eye is closed stop entering this section
        # and measure current closing eye time in order to calculate blink duration time
        if ear <= self.ear_threshold and self.closed_eye is not True:
            self.closed_eye = True
            self.close_eye_time = time.time()

        # When they eye is opened (ear > ear_threshold) after the eye was closed, start calculate the blink duration,
        # and classify if it is blink snooze or sleep symptom
        if ear > self.ear_threshold and self.closed_eye is True:
            self.closed_eye = False
            self.open_eye_time = time.time()

            # Blink duration calculated by the difference of close eye time and the open eye time
            blink_duration_time = self.open_eye_time - self.close_eye_time

            # Classify which symptom it is by blink duration time
            self._blink_detection(blink_duration_time)
            self._snooze_detection(blink_duration_time)

    def mouth_symptoms_classification(self, mar):
        """
        Description: Classification of mouth symptoms using the mouth aspect ratio and open mouth duration
        :param mar:
        :return:
        """

        if mar > self.mar_threshold and self.open_mouth is not True:
            self.open_mouth = True
            self.open_mouth_time = time.time()

        if mar < self.mar_threshold and self.open_mouth is True:
            self.open_mouth = False
            self.close_mouth_time = time.time()
            yaw_duration_time = self.close_mouth_time - self.open_mouth_time

            self.yawning_detection(yaw_duration_time)

    def _blink_detection(self, blink_duration):
        """
        Description: Detect if a blink occur by the closed eye duration
        :param blink_duration:
        :return:
        """

        if 0.05 < blink_duration < 0.15:
            self.blinks_per_minuets += 1
        if self.blinks_per_minuets > 25:
            self.blinking_hazard += 1

    def _snooze_detection(self, blink_duration):
        """
        Description: Detect if a snooze occur by the closed eye duration
        :param blink_duration:
        :return:
        """
        if 0.15 < blink_duration < 0.9:
            self.number_of_snooze += 1

    def yawning_detection(self, yaw_duration):
        """
        Description: Detect if a yaw occur by the open mouth duration
        :param yaw_duration:
        :return:
        """
        if 0.3 < yaw_duration:
            self.numbers_of_yaws += 1

    def drowsiness_detection(self):
        """
        Description: approximation of driver drowsiness using calculation of his snooze,blinks, and yaw
        :return:
        """
        if self.time_window_seconds > 60:
            print(f"blinks per minutes: {self.blinks_per_minuets}")
            self.blinks_per_minuets = 0
            self.time_window_minutes += 1
            self.starting_time_window = 0
            self.time_window_seconds = 0

        if self.time_window_minutes >= 1:
            self.drowsy_indicator = self.blinking_hazard * 0.5 + self.numbers_of_yaws * 0.8 + self.number_of_snooze * 0.8
            self.blinking_hazard = 0
            self.number_of_snooze = 0
            self.numbers_of_yaws = 0
            self.time_window_minutes = 0
            self.start_voice_flag = True
            print(f"Drowsy 5 minutes indicator: {self.drowsy_indicator}")
            if self.drowsy_indicator >= 10:
                self.drowsy_level += 1
            elif self.drowsy_level > 0:
                self.drowsy_level -= 1

        if self.starting_time_window == 0:
            self.starting_time_window = time.time()

        self.time_window_seconds = time.time() - self.starting_time_window
