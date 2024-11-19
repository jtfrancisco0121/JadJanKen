import cv2
from app.simple_facerec import SimpleFacerec

# Encode faces from a folder
sfr = SimpleFacerec()
sfr.load_encoding_images("images/")

# Load Camera (default to index 0 if index 2 fails)
cap = cv2.VideoCapture(2)  # Try accessing camera at index 2

if not cap.isOpened():  # If index 2 fails, fallback to index 0
    print("Camera index 2 not available. Trying index 0.")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():  # If still not available, exit
    print("Error: No accessible camera found.")
    exit()

while True:
    ret, frame = cap.read()

    # Check if frame is valid
    if not ret or frame is None:
        print("Error: Unable to capture video frame.")
        break

    # Detect Faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    for face_loc, name in zip(face_locations, face_names):
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        # Draw rectangle and text on frame
        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

    # Display the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop on pressing 'ESC'
    key = cv2.waitKey(1)
    if key == 27:  # ESC key
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
