import time


class FatigueDetector:
    blinks_per_minuets = 0
    numbers_of_yaws = 0
    number_of_snooze = 0
    time_window = 0
    starting_time_window = 0
    drowsy_indicator = 0
    ear_threshold = 0.2
    closed_eye = False
    isDrowsy = False
    close_eye_time = 0
    open_eye_time = 0

    def eyes_symptoms_classification(self, ear):
        """

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

    def _blink_detection(self, blink_duration):
        """
        :return:
        """
        if 0.02 < blink_duration < 0.3:
            self.blinks_per_minuets += 1

    def _snooze_detection(self, blink_duration):
        """
        :return:
        """
        if 0.3 < blink_duration < 1:
            self.number_of_snooze += 1

    def yawning_detection(self, mouth):
        """
        :return:
        """

    def drowsiness_detection(self):
        """
        :return:
        """
        if self.time_window > 10:
            print(f"Drowsy indicator: {self.drowsy_indicator}")
            self.blinks_per_minuets = 0
            self.starting_time_window = 0
            self.number_of_snooze = 0
            self.numbers_of_yaws = 0

        if self.starting_time_window == 0:
            self.starting_time_window = time.time()

        self.time_window = time.time() - self.starting_time_window

        self.drowsy_indicator = ((self.blinks_per_minuets / 4) / 3) + \
                                (self.numbers_of_yaws / 3) + \
                                (self.number_of_snooze / 3)
