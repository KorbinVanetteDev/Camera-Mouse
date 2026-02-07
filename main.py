import cv2
import mediapipe as mp
import numpy as np

video = cv2.VideoCapture(0)

# Use older API with better settings
hands = mp.solutions.hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)
drawing = mp.solutions.drawing_utils

if not video.isOpened():
    print("Oh noooo it didn't open :(")
    exit()

print("Yay it opened! Press 'q' to quit.")
print("Make sure your hands are visible and well-lit!")

# Cube settings
default_cube_size = 160
min_cube_size = 80
max_cube_size = 320
scale_speed = 0.2

# Cubes list
cubes = [
    {"x": 320, "y": 240, "size": default_cube_size, "grabbed": False, "grab_offset_x": 0, "grab_offset_y": 0}
]
active_type = None
active_index = None
prev_hand_dist = None

# Spheres list
default_sphere_radius = 80
min_sphere_radius = 40
max_sphere_radius = 160
spheres = [
    {"x": 520, "y": 240, "r": default_sphere_radius, "grabbed": False, "grab_offset_x": 0, "grab_offset_y": 0}
]

# Triangles list
default_triangle_size = 140
min_triangle_size = 60
max_triangle_size = 280
triangles = [
    {"x": 420, "y": 360, "size": default_triangle_size, "grabbed": False, "grab_offset_x": 0, "grab_offset_y": 0}
]

# Add cube button
button_x, button_y = 20, 20
button_w, button_h = 160, 50
add_pressed = False

# Add sphere button
sphere_btn_x, sphere_btn_y = 200, 20
sphere_btn_w, sphere_btn_h = 170, 50
add_sphere_pressed = False

# Add triangle button
tri_btn_x, tri_btn_y = 390, 20
tri_btn_w, tri_btn_h = 190, 50
add_triangle_pressed = False

while True:
    maybeOn, frame = video.read()

    if not maybeOn:
        print("Oh noooo I couldn't read a frame :(")
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    
    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = hands.process(rgb_frame)
    
    # Track per-hand info
    hand_info = {}
    
    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp.solutions.hands.HAND_CONNECTIONS,
                drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=4),
                drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
            )
            
            # Get thumb tip and index finger tip positions
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            
            # Convert to pixel coordinates
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
            
            # Calculate midpoint
            mid_x = (thumb_x + index_x) // 2
            mid_y = (thumb_y + index_y) // 2
            
            # Calculate distance
            distance = np.sqrt((thumb_x - index_x)**2 + (thumb_y - index_y)**2)
            
            # Determine handedness label if available
            label = None
            if results.multi_handedness and i < len(results.multi_handedness):
                label = results.multi_handedness[i].classification[0].label

            # Pinch state
            is_pinching = distance <= 80

            # Draw red/green dot
            if not is_pinching:
                cv2.circle(frame, (mid_x, mid_y), 20, (0, 0, 255), -1)  # Red dot
            else:
                cv2.circle(frame, (mid_x, mid_y), 20, (0, 255, 0), -1)  # Green dot

            if label:
                hand_info[label] = {
                    "x": mid_x,
                    "y": mid_y,
                    "pinching": is_pinching
                }
            else:
                hand_info[f"Unknown_{i}"] = {
                    "x": mid_x,
                    "y": mid_y,
                    "pinching": is_pinching
                }

    # Resolve left/right if labels missing (use x-position)
    left = hand_info.get("Left")
    right = hand_info.get("Right")
    if left is None or right is None:
        unknown = [v for k, v in hand_info.items() if k.startswith("Unknown_")]
        if len(unknown) >= 2:
            unknown = sorted(unknown, key=lambda h: h["x"])
            left = unknown[0]
            right = unknown[1]

    # Add cube button (pinch to add)
    add_clicked = False
    for hand in [left, right]:
        if hand and hand["pinching"]:
            if button_x <= hand["x"] <= (button_x + button_w) and button_y <= hand["y"] <= (button_y + button_h):
                add_clicked = True
                break
    if add_clicked and not add_pressed:
        cubes.append({
            "x": int(w * 0.6),
            "y": int(h * 0.5),
            "size": default_cube_size,
            "grabbed": False,
            "grab_offset_x": 0,
            "grab_offset_y": 0
        })
    add_pressed = add_clicked

    # Add sphere button (pinch to add)
    add_sphere_clicked = False
    for hand in [left, right]:
        if hand and hand["pinching"]:
            if sphere_btn_x <= hand["x"] <= (sphere_btn_x + sphere_btn_w) and sphere_btn_y <= hand["y"] <= (sphere_btn_y + sphere_btn_h):
                add_sphere_clicked = True
                break
    if add_sphere_clicked and not add_sphere_pressed:
        spheres.append({
            "x": int(w * 0.4),
            "y": int(h * 0.5),
            "r": default_sphere_radius,
            "grabbed": False,
            "grab_offset_x": 0,
            "grab_offset_y": 0
        })
    add_sphere_pressed = add_sphere_clicked

    # Add triangle button (pinch to add)
    add_triangle_clicked = False
    for hand in [left, right]:
        if hand and hand["pinching"]:
            if tri_btn_x <= hand["x"] <= (tri_btn_x + tri_btn_w) and tri_btn_y <= hand["y"] <= (tri_btn_y + tri_btn_h):
                add_triangle_clicked = True
                break
    if add_triangle_clicked and not add_triangle_pressed:
        triangles.append({
            "x": int(w * 0.7),
            "y": int(h * 0.6),
            "size": default_triangle_size,
            "grabbed": False,
            "grab_offset_x": 0,
            "grab_offset_y": 0
        })
    add_triangle_pressed = add_triangle_clicked

    # Grabbing: right hand only (inside cube, sphere, or triangle)
    if right and right["pinching"]:
        if active_index is None:
            # Check cubes (topmost last)
            for idx in reversed(range(len(cubes))):
                cube = cubes[idx]
                half = cube["size"] // 2
                if (cube["x"] - half) <= right["x"] <= (cube["x"] + half) and (cube["y"] - half) <= right["y"] <= (cube["y"] + half):
                    active_type = "cube"
                    active_index = idx
                    cube["grabbed"] = True
                    cube["grab_offset_x"] = cube["x"] - right["x"]
                    cube["grab_offset_y"] = cube["y"] - right["y"]
                    break
            # Check spheres if no cube grabbed
            if active_index is None:
                for idx in reversed(range(len(spheres))):
                    sphere = spheres[idx]
                    dx = right["x"] - sphere["x"]
                    dy = right["y"] - sphere["y"]
                    if (dx * dx + dy * dy) <= sphere["r"] * sphere["r"]:
                        active_type = "sphere"
                        active_index = idx
                        sphere["grabbed"] = True
                        sphere["grab_offset_x"] = sphere["x"] - right["x"]
                        sphere["grab_offset_y"] = sphere["y"] - right["y"]
                        break
            # Check triangles if no shape grabbed
            if active_index is None:
                for idx in reversed(range(len(triangles))):
                    tri = triangles[idx]
                    half = tri["size"] // 2
                    if (tri["x"] - half) <= right["x"] <= (tri["x"] + half) and (tri["y"] - half) <= right["y"] <= (tri["y"] + half):
                        active_type = "triangle"
                        active_index = idx
                        tri["grabbed"] = True
                        tri["grab_offset_x"] = tri["x"] - right["x"]
                        tri["grab_offset_y"] = tri["y"] - right["y"]
                        break
        if active_index is not None:
            if active_type == "cube":
                cube = cubes[active_index]
                cube["x"] = right["x"] + cube["grab_offset_x"]
                cube["y"] = right["y"] + cube["grab_offset_y"]
            elif active_type == "sphere":
                sphere = spheres[active_index]
                sphere["x"] = right["x"] + sphere["grab_offset_x"]
                sphere["y"] = right["y"] + sphere["grab_offset_y"]
            elif active_type == "triangle":
                tri = triangles[active_index]
                tri["x"] = right["x"] + tri["grab_offset_x"]
                tri["y"] = right["y"] + tri["grab_offset_y"]
    else:
        if active_index is not None:
            if active_type == "cube":
                cubes[active_index]["grabbed"] = False
            elif active_type == "sphere":
                spheres[active_index]["grabbed"] = False
            elif active_type == "triangle":
                triangles[active_index]["grabbed"] = False
        active_type = None
        active_index = None

    # Scaling: left hand pinching controls scale by distance to active shape center
    if left and left["pinching"] and active_index is not None:
        if active_type == "cube":
            cube = cubes[active_index]
            dist = np.sqrt((left["x"] - cube["x"]) ** 2 + (left["y"] - cube["y"]) ** 2)
            if prev_hand_dist is not None:
                delta = dist - prev_hand_dist
                cube["size"] = int(np.clip(cube["size"] + delta * scale_speed, min_cube_size, max_cube_size))
            prev_hand_dist = dist
        elif active_type == "sphere":
            sphere = spheres[active_index]
            dist = np.sqrt((left["x"] - sphere["x"]) ** 2 + (left["y"] - sphere["y"]) ** 2)
            if prev_hand_dist is not None:
                delta = dist - prev_hand_dist
                sphere["r"] = int(np.clip(sphere["r"] + delta * scale_speed, min_sphere_radius, max_sphere_radius))
            prev_hand_dist = dist
        elif active_type == "triangle":
            tri = triangles[active_index]
            dist = np.sqrt((left["x"] - tri["x"]) ** 2 + (left["y"] - tri["y"]) ** 2)
            if prev_hand_dist is not None:
                delta = dist - prev_hand_dist
                tri["size"] = int(np.clip(tri["size"] + delta * scale_speed, min_triangle_size, max_triangle_size))
            prev_hand_dist = dist
    else:
        prev_hand_dist = None

    # Draw cubes (yellow when grabbed, blue when free)
    for cube in cubes:
        cube_color = (0, 255, 255) if cube["grabbed"] else (255, 0, 0)
        cv2.rectangle(
            frame,
            (cube["x"] - cube["size"] // 2, cube["y"] - cube["size"] // 2),
            (cube["x"] + cube["size"] // 2, cube["y"] + cube["size"] // 2),
            cube_color,
            6
        )

    # Draw spheres (yellow when grabbed, blue when free)
    for sphere in spheres:
        sphere_color = (0, 255, 255) if sphere["grabbed"] else (255, 0, 0)
        cv2.circle(frame, (sphere["x"], sphere["y"]), sphere["r"], sphere_color, 6)

    # Draw triangles (yellow when grabbed, blue when free)
    for tri in triangles:
        tri_color = (0, 255, 255) if tri["grabbed"] else (255, 0, 0)
        size = tri["size"]
        pts = np.array([
            [tri["x"], tri["y"] - size // 2],
            [tri["x"] - size // 2, tri["y"] + size // 2],
            [tri["x"] + size // 2, tri["y"] + size // 2]
        ], dtype=np.int32)
        cv2.polylines(frame, [pts], True, tri_color, 6)

    # Draw Add Cube button
    button_color = (0, 200, 0) if add_pressed else (0, 150, 0)
    cv2.rectangle(frame, (button_x, button_y), (button_x + button_w, button_y + button_h), button_color, -1)
    cv2.putText(frame, "Add Cube", (button_x + 10, button_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Draw Add Sphere button
    sphere_button_color = (0, 200, 0) if add_sphere_pressed else (0, 150, 0)
    cv2.rectangle(frame, (sphere_btn_x, sphere_btn_y), (sphere_btn_x + sphere_btn_w, sphere_btn_y + sphere_btn_h), sphere_button_color, -1)
    cv2.putText(frame, "Add Sphere", (sphere_btn_x + 10, sphere_btn_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Draw Add Triangle button
    tri_button_color = (0, 200, 0) if add_triangle_pressed else (0, 150, 0)
    cv2.rectangle(frame, (tri_btn_x, tri_btn_y), (tri_btn_x + tri_btn_w, tri_btn_y + tri_btn_h), tri_button_color, -1)
    cv2.putText(frame, "Add Triangle", (tri_btn_x + 10, tri_btn_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("Going to be a mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
hands.close()