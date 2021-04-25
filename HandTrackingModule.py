import cv2
import mediapipe as mp
import time


class HandDetector():
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.max_hands, self.detection_con, self.track_con)
        # for drawing landmarks
        self.mpDraw = mp.solutions.drawing_utils

        self.cx4 = 0
        self.cy4 = 0
        self.cx8 = 0
        self.cy8 = 0

    def find_hands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, drawing_fingers, hand_no=0, draw=True):
        lm_list = []

        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                # height and width
                h, w, c = img.shape
                # get position
                cx, cy = int(lm.x*w), int(lm.y*h)
                lm_list.append([id, cx, cy])
                if draw:
                    if id in drawing_fingers:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            return lm_list


def main():
    p_time = 0
    c_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while True:
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_position(img, [4, 8])

        if lm_list is not None and len(lm_list) != 0:
            print(lm_list[0])

        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
