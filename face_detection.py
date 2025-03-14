import cv2

# Loading pre-trained face detection model (Haar cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Starting the webcam
cap = cv2.VideoCapture(0)

# Checking if the camera has started
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

frame_count = 0
while True:
    # Frame-by-frame capturing
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break
    
    frame_count += 1
    if frame_count % 3 != 0:  # Process every 3rd frame to reduce lag
        continue
    
    # Resizing frame to reduce processing time and lag
    frame = cv2.resize(frame, (640, 480))

    # Converting to grayscale as face detection works better on b/w images
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecting faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    # If no frontal face detected, try profile face detection
    if len(faces) == 0:
        faces = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        if len(faces) == 0:
            flipped_gray = cv2.flip(gray, 1)  # Flip image for the opposite profile face
            faces = profile_cascade.detectMultiScale(flipped_gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
    
    # Drawing a single box around the largest detected face
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])  # Select largest face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    cv2.imshow('Face Detection', frame)

    # Pressing 'q' will break the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
