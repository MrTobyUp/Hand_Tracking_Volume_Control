import HandTrackingModule as htm
import FingerCounter as finCoun
import cv2
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


class VolumeControll:
    def __init__(self):
        self.selected_volume = 0

    def get_finger_distance(self, lm_list):
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
            return volume

    def set_audio_volume(self, selected_volume):
        # Get default audio device using PyCAW
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if selected_volume is not None:
            new_volume = -63.5 * math.pow(0.96428460868, selected_volume)
            volume.SetMasterVolumeLevel(new_volume, None)

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


def main():
    cap = cv2.VideoCapture(0)
    detector = htm.HandDetector()
    volume_con = VolumeControll()
    finger_counter = finCoun.FingerCounter()
    displayed_volume = 0

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, [4, 8])

        img = volume_con.draw_key_objects(img, lm_list)

        selected_volume = volume_con.get_finger_distance(lm_list)
        print(selected_volume)

        fingers_raised = finger_counter.get_raised_fingers(lm_list)
        if fingers_raised is not None and len(fingers_raised) != 0:
            if 2 in fingers_raised:
                volume_con.set_audio_volume(selected_volume)
                displayed_volume = selected_volume

        cv2.putText(img, f'{str(displayed_volume)}%', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
