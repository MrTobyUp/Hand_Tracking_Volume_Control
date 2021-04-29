import HandTrackingModule as htm
import FingerCounter as finCoun
import cv2
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


class VolumeControll:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.detector = htm.HandDetector()
        self.finger_counter = finCoun.FingerCounter()
        self.selected_volume = 0
        self.displayed_volume = 0
        self.old_volume = 0
        self.hand_in_image = False

    def calculate_finger_distance(self, lm_list):
        if lm_list is not None and len(lm_list) != 0:
            x_dist = abs(lm_list[4][1]-lm_list[8][1])
            y_dist = abs(lm_list[4][2] - lm_list[8][2])

            distance = int(math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2)))
            # 30: min if fingers are together
            # 1.7: 170(fingers spread) / 100
            volume = int((distance - 30) / 1.7)
            if volume < 0:
                volume = 0
            elif volume > 100:
                volume = 100
            self.selected_volume = volume

    def set_audio_volume(self):
        # Get default audio device using PyCAW
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if self.selected_volume is not None:
            new_volume = -63.5 * math.pow(0.96428460868, self.selected_volume)
            volume.SetMasterVolumeLevel(new_volume, None)

    def get_audio_volume(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        decibel = volume.GetMasterVolumeLevel()
        if decibel > 0:
            decibel = 0
        elif decibel < -63.49:
            decibel = -63.49

        percent = int(math.log(decibel / -63.5, 0.96428460868))
        return int

    def distance_calibrate(self, lm_list):
        if lm_list is not None and len(lm_list) != 0:
            x_dist = abs(lm_list[4][1] - lm_list[8][1])
            y_dist = abs(lm_list[4][2] - lm_list[8][2])

            distance = int(math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2)))
            print("distance %s", str(distance))

    def draw_key_objects(self, img, lm_list):
        if lm_list is not None and len(lm_list) != 0:
            cx4 = lm_list[4][1]
            cy4 = lm_list[4][2]
            cx8 = lm_list[8][1]
            cy8 = lm_list[8][2]

            if self.selected_volume < 33:
                cv2.line(img, (cx4, cy4), (cx8, cy8), (0, 128, 0), 3)
            elif self.selected_volume < 66:
                cv2.line(img, (cx4, cy4), (cx8, cy8), (51, 153, 255), 3)
            else:
                cv2.line(img, (cx4, cy4), (cx8, cy8), (0, 0, 128), 3)

        return img

    def calibrate_hand(self):
        hand_found_count = 0
        while hand_found_count < 15:
            success, img = self.cap.read()
            img = self.detector.find_hands(img, False)
            # img = self.detector.draw_calibrate(img)
            hand = self.detector.find_position(img)

            if hand is not None and len(hand) != 0:
                hand_found_count += 1
            else:
                hand_found_count = 0

            # self.displayed_volume = self.get_audio_volume()
            cv2.putText(img, f'{str(self.displayed_volume)}%', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
            cv2.putText(img, f'searching', (10, 100), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)

            cv2.imshow("Image", img)
            cv2.waitKey(1)
        self.hand_in_image = True

    def controll_volume(self):
        success, img = self.cap.read()
        img = self.detector.find_hands(img, False)
        lm_list = self.detector.find_position(img, [4, 8])

        # Check if hand leaves the image: yes => calibrate
        if lm_list is None:
            self.hand_in_image = False

        img = self.draw_key_objects(img, lm_list)

        self.calculate_finger_distance(lm_list)

        fingers_raised = self.finger_counter.get_raised_fingers(lm_list)
        if fingers_raised is not None and len(fingers_raised) != 0:
            # to be more consistent
            if 2 in fingers_raised and self.old_volume == self.selected_volume:
                self.set_audio_volume()
                self.displayed_volume = self.selected_volume

        self.old_volume = self.selected_volume
        cv2.putText(img, f'{str(self.displayed_volume)}%', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
        return img

    def get_hand_in_image_status(self):
        return self.hand_in_image


def main():
    volume_con = VolumeControll()
    while True:
        if not volume_con.get_hand_in_image_status():
            volume_con.calibrate_hand()
        else:
            img = volume_con.controll_volume()
            cv2.imshow("Image", img)
            cv2.waitKey(1)


if __name__ == "__main__":
    main()
