# Camera Mouse

This project is a browser port of the original Python OpenCV + MediaPipe app. It runs entirely in the browser and uses your webcam to detect hand pinches, then lets you grab and scale shapes on a canvas.

## How it works

- **Webcam input** is captured with MediaPipe Camera Utils.
- **MediaPipe Hands** detects hand landmarks each frame.
- The input frame is **flipped horizontally** before processing, matching the original Python `cv2.flip` behavior.
- **Pinch detection**: the distance between thumb tip (landmark 4) and index tip (landmark 8) is measured. If the distance is below the pinch threshold, the hand is considered pinching.
- **Left/Right hand logic**:
	- If MediaPipe provides handedness, it is **swapped** because the input is flipped before processing.
	- If only one hand is visible, it is treated as the **grab hand**.
- **Grab behavior** (right hand in the original):
	- When pinching inside a shape, the shape is grabbed.
	- While pinching, the shape follows the hand with an offset.
- **Scale behavior** (left hand in the original):
	- When two hands are visible, the left hand pinches to scale the active shape.
	- Scale is based on the distance between the left hand and the active shape center.
- **Buttons** (pinch to activate):
	- Add Cube
	- Add Sphere
	- Add Triangle

## Files

- [index.html](index.html): Loads MediaPipe, canvas, and scripts.
- [style.css](style.css): Fullscreen canvas styling.
- [app.js](app.js): Main logic (camera, hand tracking, pinch detection, grabbing, scaling, drawing).

## Run locally

A webcam app must run on HTTPS or localhost. The easiest way is a local server:

1. Start a server in this folder.
2. Open http://localhost:8000 in your browser.

## Controls

- **Pinch** to interact.
- **Right hand** grabs shapes.
- **Left hand** scales shapes (when both hands are visible).
- **Pinch buttons** to add new shapes.

## Notes

- If grabbing feels unstable, adjust pinch thresholds and smoothing in [app.js](app.js).
- Make sure your hands are well-lit and fully visible to the camera.
