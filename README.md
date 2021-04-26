# Hand Tracking Volume Control
Project to change the volume with your fingers. By moving together and apart.

### New Feature:
The volume only changes when the middle finger is raised. So the volume can remain the same without holding your hand up.

## Visualisation
To see, whats going on, the image of your camera is getting displayed. Additionally the landmarks are drawn over it, to visualize how to move your fingers.

<img src="https://picr.eu/images/2021/04/24/QcNOI.png" alt="QcNOI.png" border="0" />

By moving the purple colored fingers, you change the volume on the computer.

## Hand detection
Mediapipe was used for hand recognition. In the graphic you can see the individual landmarks and the corresponding numbers
![QccMk.png](https://picr.eu/images/2021/04/25/QccMk.png)

Source: https://google.github.io/mediapipe/solutions/hands

## Infos
The project was created with python in combination with opencv and mediapipe.
