import HandTrackingModule as htm
import cv2
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


class VolumeControll:
    def __init__(self):
        pass

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


def main():
    cap = cv2.VideoCapture(0)
    detector = htm.HandDetector()
    volume_con = VolumeControll()

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_position(img)

        selected_volume = volume_con.get_finger_distance(lm_list)
        print(selected_volume)
        volume_con.set_audio_volume(selected_volume)

        cv2.putText(img, str(selected_volume), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
