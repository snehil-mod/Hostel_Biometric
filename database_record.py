import cv2
import face_recognition
from pymongo import MongoClient
from datetime import datetime

#MongoDB connection setup
def get_db():

    #connecting to the MongoDB Compass server
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Hostel_Attendance"] #Database for all hostel related data
    attendance_collection = db["Attendance_records"] #collection to store attendance records

    return attendance_collection

def recognize_faces(frame, known_face_encodings, known_face_names):
    #converting the image from BGR to RGB:
    rgb_frame = frame[:,:,::-1] #reversing the color B-G-R to R-G-B

    #finding all the face locations and encodings in the frane:
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    #Listing of names of recognized faces
    face_names = []

    for face_encoding in face_encodings:
        #checking if the face matches the database:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        #Using the known face with the smallest distance
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names(first_match_index)

        face_names.append(name)

    return face_locations, face_names



if __name__ == "__main__":
    #collecting attendance from mongodb
    attendance_collection = get_db()
    
    
    known_face_names = ["Snehil Singh", "Dev Mishra"]
    known_face_encodings = []

    #loading and encoding known faces
    for name in known_face_names:
        image = face_recognition.load_image_file(f"{name}.jpg") #loading image file of the known person
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
    
    #starting video
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Could not read frame")
            break

        #detect and recognize face:
        face_locations, face_names = recognize_faces(frame, known_face_encodings, known_face_names)

        #Displaying results:
        for(top, right, bottom, left), name in zip(face_locations, face_names):
            #drawing rectangle around face
            cv2.rectangle(frame, (left,top), (right, bottom), (0,0,255), 2)
            #Label the face
            cv2.putText(frame, name,(left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            #marking attendance if unrecognized:
            if name!= "unknown":
                attendance_time = datetime.now().strftime("%H:%M")
                attendance_record = {
                    "Name": name,
                    "Roll No": 22052509,
                    "Attendance": True,
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Time of Attendance": attendance_time
                }
                attendance_collection.insert_one(attendance_record)
                print("Attendance recorded: ", attendance_record)

        #displaying the resulting frame:
        cv2.imshow('Video', frame)

        #break the loop if key = q is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()