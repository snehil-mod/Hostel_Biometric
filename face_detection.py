import cv2

#loading pre-trained face detection model named as Haar cascade
# For frontal faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# For profile faces (side angles)
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

#starting the cam
cap = cv2.VideoCapture(0)

#checking if cam has started
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    #frame by frame capturing
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame")
        break

    #Resizing frame to reduce processing time and lag
    frame = cv2.resize(frame, (640, 480))

    #converting to grayscale as fd works better on b/w images
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #detecting faces in the frame
    #for front angle
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors = 10, minSize = (90,90))

    #for side angle,
    profile = profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors = 10, minSize = (80,80))

    #we need to capture both the side angles of face so,
    flipped_gray = cv2.flip(gray, 1)
    flipped_profile = profile_cascade.detectMultiScale(flipped_gray, scaleFactor=1.05, minNeighbors=10, minSize=(80,80))
    
    #drawing rectangles around the face
    #for frontal angle
    for(x,y,p,q) in faces:
        cv2.rectangle(frame, (x,y), (x+p, y+q), (255,0,0), 2)
    #for side angle
    for(x,y,p,q) in profile:
        cv2.rectangle(frame, (x,y), (x+p, y+p), (0,255,0), 2)
    #for side angle flipped<
    for(x,y,p,q) in flipped_profile:
        x = frame.shape[1] - x - p
        cv2.rectangle(frame, (x,y), (x+p, y+p), (0,255,0), 2)


    cv2.imshow('Face Detection', frame)

    #pressing q will break loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()