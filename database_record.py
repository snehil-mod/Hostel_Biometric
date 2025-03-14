import cv2
import face_recognition
from pymongo import MongoClient
from datetime import datetime
import os
import numpy as np
import time
import pyttsx3
from collections import deque
import threading
import queue

# Global variables for threading
speech_queue = queue.Queue()
speech_thread_running = False

# Speech thread function
def speech_thread_function(engine):
    global speech_thread_running
    speech_thread_running = True
    while speech_thread_running:
        try:
            # Get text from queue with timeout to allow thread to exit
            text = speech_queue.get(timeout=1.0)
            if text == "EXIT":
                break
            engine.say(text)
            engine.runAndWait()
            speech_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Error in speech thread: {str(e)}")
    print("Speech thread exiting")

# Initialize text-to-speech engine
def init_voice_engine():
    try:
        engine = pyttsx3.init()
        # Set properties
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Start speech thread
        speech_thread = threading.Thread(target=speech_thread_function, args=(engine,), daemon=True)
        speech_thread.start()
        
        return engine
    except Exception as e:
        print(f"Warning: Could not initialize voice engine: {str(e)}")
        return None

# Function to speak text without blocking
def speak_text(engine, text):
    if engine:
        try:
            # Add text to queue for speech thread to process
            speech_queue.put(text)
        except Exception as e:
            print(f"Error queuing text for speech: {str(e)}")

# MongoDB connection setup
def get_db():
    # connecting to the MongoDB Compass server
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["Hostel_Attendance"]  # Database for all hostel related data
        attendance_collection = db["Attendance_records"]  # collection to store attendance records
        students_collection = db["Students"]  # collection to store student information
        return db, attendance_collection, students_collection, True
    except Exception as e:
        print("Error: Could not connect to MongoDB:", e)
        return None, None, None, False

# Pre-load the face cascade classifier to avoid loading it repeatedly
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Function to detect faces using OpenCV's Haar cascade - optimized version
def detect_faces(frame):
    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with optimized parameters
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.3,      # Higher value for faster detection but less accuracy
        minNeighbors=5,       # Higher value means fewer false positives
        minSize=(30, 30),     # Minimum face size
        flags=cv2.CASCADE_SCALE_IMAGE  # Use image pyramid for better performance
    )
    
    # Return face locations in (top, right, bottom, left) format to match face_recognition library
    face_locations = []
    for (x, y, w, h) in faces:
        face_locations.append((y, x + w, y + h, x))
    
    return face_locations

# Function to recognize faces - optimized version
def recognize_faces(frame, known_face_encodings, known_face_names):
    # Detect faces using OpenCV
    face_locations = detect_faces(frame)
    
    # If no faces are detected, return empty lists
    if not face_locations:
        return [], []
    
    # Convert frame from BGR to RGB for face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Initialize face names
    face_names = ["Unknown"] * len(face_locations)
    
    # Try to use face_recognition if we have known faces
    if known_face_encodings:
        try:
            # Get face encodings for detected faces
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # Compare each face with known faces
            for i, face_encoding in enumerate(face_encodings):
                try:
                    # Compare with known faces
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                    
                    # If a match is found, use the name of the first match
                    if True in matches:
                        first_match_index = matches.index(True)
                        face_names[i] = known_face_names[first_match_index]
                except Exception as e:
                    print(f"Error comparing face {i}: {str(e)}")
        except Exception as e:
            print(f"Error encoding faces: {str(e)}")
    
    return face_locations, face_names

# Function to verify student by roll number
def verify_student_by_id(students_collection, roll_number):
    try:
        # Check if the roll number exists in the database
        student = students_collection.find_one({"Roll No": roll_number})
        if student:
            return True, student["Name"]
        return False, None
    except Exception as e:
        print(f"Error verifying student: {str(e)}")
        return False, None

# Function to handle manual authorization
def manual_authorization(students_collection):
    print("\n--- Manual Authorization Required ---")
    roll_number = input("Please enter your Roll Number: ")
    
    try:
        # Verify the roll number
        is_valid, name = verify_student_by_id(students_collection, int(roll_number))
        
        if is_valid:
            print(f"Authorization successful. Welcome, {name}!")
            return True, name, int(roll_number)
        else:
            print("Authorization failed. Roll Number not found in database.")
            return False, None, None
    except ValueError:
        print("Invalid input. Please enter a numeric Roll Number.")
        return False, None, None

# Function to add a new face to the database
def register_new_face(frame, name, roll_number):
    try:
        # Save the face image
        filename = f"{name.replace(' ', '_')}.jpg"  # Use name as filename for easier loading
        image_path = os.path.join(r"E:\Projects\Hostel_Biometric\hostel_biometric_env", filename)
        
        # Resize and save the image
        cv2.imwrite(image_path, frame)
        print(f"✅ Face image saved as {filename}")
        
        return True
    except Exception as e:
        print(f"❌ Error registering new face: {str(e)}")
        return False

# Function to load face encodings for known students
def load_face_encodings(known_face_names):
    known_face_encodings = []
    base_path = r"E:\Projects\Hostel_Biometric\hostel_biometric_env"
    
    for name in known_face_names:
        image_path = os.path.join(base_path, f"{name}.jpg")
        
        if os.path.exists(image_path):
            try:
                print(f"Loading image for {name}...")
                image = face_recognition.load_image_file(image_path)
                
                try:
                    # Try to get face encodings
                    encodings = face_recognition.face_encodings(image)
                    
                    if encodings and len(encodings) > 0:
                        known_face_encodings.append(encodings[0])
                        print(f"✅ Successfully encoded face for {name}")
                    else:
                        print(f"⚠ Warning: No face detected in {image_path}. Skipping...")
                except Exception as e:
                    print(f"❌ Error encoding face for {name}: {str(e)}")
            except Exception as e:
                print(f"❌ Error loading image for {name}: {str(e)}")
        else:
            print(f"❌ Error: Image file '{image_path}' not found! Make sure it's in the correct folder.")
    
    return known_face_encodings

# Function to initialize the database with sample data if needed
def init_database(students_collection):
    if students_collection.count_documents({}) == 0:
        sample_students = [
            {"Name": "Snehil Singh", "Roll No": 22052509, "Face Registered": True},
            {"Name": "Dev Mishra", "Roll No": 22052510, "Face Registered": True},
            {"Name": "John Doe", "Roll No": 22052511, "Face Registered": False},
            {"Name": "Jane Smith", "Roll No": 22052512, "Face Registered": False}
        ]
        students_collection.insert_many(sample_students)
        print("Sample student data added to database.")

# Function to record attendance in the database
def record_attendance(attendance_collection, name, roll_no, method, entry_type):
    attendance_time = datetime.now().strftime("%H:%M")
    
    attendance_record = {
        "Name": name,
        "Roll No": roll_no,
        "Attendance": True,
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Time of Attendance": attendance_time,
        "Method": method,
        "Entry Type": entry_type
    }
    
    try:
        attendance_collection.insert_one(attendance_record)
        print("Attendance recorded: ", attendance_record)
        return True
    except Exception as e:
        print(f"Error recording attendance: {str(e)}")
        return False

# Function to handle unknown face authentication
def handle_unknown_face(video_capture, display_frame, face_id, face_location, unknown_face_counters, 
                        max_unknown_attempts, db_connected, students_collection, attendance_collection, 
                        voice_engine, cooldown_duration, known_face_encodings, known_face_names, last_entry_time):
    top, right, bottom, left = face_location
    
    # Track attempts for this unknown face
    if face_id not in unknown_face_counters:
        unknown_face_counters[face_id] = 1
    else:
        unknown_face_counters[face_id] += 1
    
    # Display attempt count
    attempt_text = f"Verifying... ({unknown_face_counters[face_id]}/{max_unknown_attempts})"
    cv2.putText(display_frame, attempt_text, (left, bottom + 25), 
              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # If max attempts reached, trigger manual authorization
    if unknown_face_counters[face_id] >= max_unknown_attempts:
        # Pause video display
        cv2.putText(display_frame, "Manual Authorization Required", (left, bottom + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imshow('Hostel Biometric System', display_frame)
        cv2.waitKey(1)
        
        # Voice feedback
        speak_text(voice_engine, "Authentication failed")
        
        if db_connected:
            # Perform manual authorization
            is_authorized, auth_name, auth_roll = manual_authorization(students_collection)
            
            if is_authorized:
                # Determine entry type
                entry_type = "Entry"  # Default
                if auth_name in last_entry_time and last_entry_time[auth_name]["type"] == "Entry":
                    entry_type = "Exit"
                
                # Record attendance
                success = record_attendance(attendance_collection, auth_name, auth_roll, "Manual ID", entry_type)
                
                if success:
                    # Update last entry time and type
                    current_time = time.time()
                    last_entry_time[auth_name] = {
                        "time": current_time,
                        "type": entry_type
                    }
                    
                    # Set cooldown info for return
                    cooldown_info = {
                        "active": True,
                        "end_time": time.time() + cooldown_duration,
                        "message": f"{entry_type} Successful: {auth_name}",
                        "color": (0, 255, 0)  # Green
                    }
                    
                    # Voice feedback
                    speak_text(voice_engine, f"{entry_type} successful. Welcome, {auth_name}")
                    
                    # Ask if user wants to register their face
                    register_face = input("Would you like to register your face for future recognition? (y/n): ")
                    if register_face.lower() == 'y':
                        # Take a clear picture
                        print("Please look at the camera for a clear picture...")
                        for countdown in range(3, 0, -1):
                            print(f"{countdown}...")
                            time.sleep(1)
                        
                        # Capture frame for registration
                        ret, reg_frame = video_capture.read()
                        if ret:
                            if register_new_face(reg_frame, auth_name, auth_roll):
                                # Update database
                                students_collection.update_one(
                                    {"Roll No": auth_roll},
                                    {"$set": {"Face Registered": True}}
                                )
                                print("Face registered successfully!")
                                
                                # Reload face encodings
                                try:
                                    image = face_recognition.load_image_file(os.path.join(
                                        r"E:\Projects\Hostel_Biometric\hostel_biometric_env", f"{auth_name}.jpg"))
                                    encodings = face_recognition.face_encodings(image)
                                    if encodings and len(encodings) > 0:
                                        known_face_encodings.append(encodings[0])
                                        known_face_names.append(auth_name)
                                        print(f"✅ Added {auth_name} to recognition database")
                                except Exception as e:
                                    print(f"❌ Error adding face to recognition database: {str(e)}")
                        else:
                            print("Failed to capture image for registration.")
                    
                    return cooldown_info, unknown_face_counters, known_face_encodings, known_face_names
            
            # If we get here, authentication failed
            cooldown_info = {
                "active": True,
                "end_time": time.time() + cooldown_duration,
                "message": "Authentication Failed",
                "color": (0, 0, 255)  # Red
            }
            
            # Voice feedback
            speak_text(voice_engine, "Authentication failed")
            
            # Reset counter for this face
            unknown_face_counters[face_id] = 0
            
            return cooldown_info, unknown_face_counters, known_face_encodings, known_face_names
    
    # If we didn't reach max attempts yet
    return None, unknown_face_counters, known_face_encodings, known_face_names

# Function to handle known face authentication
def handle_known_face(face_location, name, db_connected, students_collection, attendance_collection, 
                     voice_engine, cooldown_duration, last_entry_time, min_entry_gap, display_frame):
    top, right, bottom, left = face_location
    current_time = time.time()
    
    # Check if enough time has passed since last entry
    can_mark_entry = True
    if name in last_entry_time:
        time_since_last = current_time - last_entry_time[name]["time"]
        can_mark_entry = time_since_last >= min_entry_gap
    
    # Mark attendance if recognized and enough time has passed
    if db_connected and can_mark_entry:
        # Get roll number from database
        student = students_collection.find_one({"Name": name})
        roll_no = student["Roll No"] if student else 0
        
        # Determine if this is an entry or exit
        entry_type = "Entry"  # Default
        if name in last_entry_time and last_entry_time[name]["type"] == "Entry":
            entry_type = "Exit"
        
        # Record attendance
        success = record_attendance(attendance_collection, name, roll_no, "Facial Recognition", entry_type)
        
        if success:
            # Update last entry time and type
            last_entry_time[name] = {
                "time": current_time,
                "type": entry_type
            }
            
            # Set cooldown info for return
            cooldown_info = {
                "active": True,
                "end_time": time.time() + cooldown_duration,
                "message": f"{entry_type} Successful: {name}",
                "color": (0, 255, 0)  # Green
            }
            
            # Voice feedback
            speak_text(voice_engine, f"{entry_type} successful. Welcome, {name}")
            
            return cooldown_info, last_entry_time
    
    elif name in last_entry_time and not can_mark_entry:
        # Show message that entry was too recent
        seconds_left = int(min_entry_gap - (current_time - last_entry_time[name]["time"]))
        wait_text = f"Please wait {seconds_left}s"
        cv2.putText(display_frame, wait_text, (left, bottom + 25), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)  # Orange text
    
    # If we didn't record attendance
    return None, last_entry_time

# Function to display cooldown message
def display_cooldown(display_frame, cooldown_message, cooldown_color, cooldown_end_time, frame_start_time):
    # Center the cooldown message and make it larger
    message_size = cv2.getTextSize(cooldown_message, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)[0]
    message_x = int((display_frame.shape[1] - message_size[0]) / 2)
    message_y = int(display_frame.shape[0] / 2)
    
    # Display cooldown message
    cv2.putText(display_frame, cooldown_message, (message_x, message_y), 
              cv2.FONT_HERSHEY_SIMPLEX, 1.2, cooldown_color, 2)
    
    # Display countdown below the message
    remaining = int(cooldown_end_time - frame_start_time) + 1
    countdown_text = f"Next scan in: {remaining}s"
    countdown_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    countdown_x = int((display_frame.shape[1] - countdown_size[0]) / 2)
    
    cv2.putText(display_frame, countdown_text, (countdown_x, message_y + 40), 
              cv2.FONT_HERSHEY_SIMPLEX, 0.8, cooldown_color, 2)

# Main function
def main():
    print("Starting Hostel Biometric System...")
    start_time = time.time()
    
    # Initialize voice engine
    voice_engine = init_voice_engine()
    
    # Connect to database
    db, attendance_collection, students_collection, db_connected = get_db()
    if not db_connected:
        print("Failed to connect to MongoDB. Continuing without database functionality.")
    else:
        # Initialize database if needed
        init_database(students_collection)
    
    # System parameters
    last_entry_time = {}  # Track last entry time for each person
    min_entry_gap = 60  # Minimum seconds between entries (1 minute)
    unknown_face_counters = {}  # Track unknown faces and their attempt counts
    max_unknown_attempts = 5  # Maximum number of attempts before manual authorization
    cooldown_duration = 3.0  # 3 seconds cooldown
    
    # Get all students with registered faces
    known_face_names = []
    
    # Loading student names
    if db_connected:
        registered_students = students_collection.find({"Face Registered": True})
        for student in registered_students:
            known_face_names.append(student["Name"])
    else:
        known_face_names = ["Snehil Singh", "Dev Mishra"]
    
    # Load face encodings
    known_face_encodings = load_face_encodings(known_face_names)
    
    # Initialize camera
    print("Initializing camera...")
    video_capture = cv2.VideoCapture(0)
    
    # Set camera properties for better performance
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    video_capture.set(cv2.CAP_PROP_FPS, 30)
    video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not video_capture.isOpened():
        print("Error: Could not access the camera")
        exit()
    
    # Performance variables
    frame_count = 0
    process_every_n_frames = 8  # Process every 8th frame for better performance
    last_process_time = time.time()
    fps_values = deque(maxlen=10)
    processing_times = deque(maxlen=10)
    
    # Cooldown state
    cooldown_active = False
    cooldown_end_time = 0
    cooldown_message = ""
    cooldown_color = (0, 255, 0)  # Default green
    
    # Create window
    cv2.namedWindow('Hostel Biometric System', cv2.WINDOW_NORMAL)
    
    # Startup complete
    startup_time = time.time() - start_time
    print(f"System initialized in {startup_time:.2f} seconds")
    
    try:
        while True:
            # Capture frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Timing
            frame_start_time = time.time()
            frame_time_elapsed = frame_start_time - last_process_time
            instantaneous_fps = 1.0 / frame_time_elapsed if frame_time_elapsed > 0 else 0
            last_process_time = frame_start_time
            fps_values.append(min(instantaneous_fps, 60))
            
            # Create display frame
            display_frame = frame.copy()
            cv2.putText(display_frame, "Hostel Biometric System", (10, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Handle cooldown period
            if cooldown_active:
                if frame_start_time < cooldown_end_time:
                    # Display cooldown message
                    display_cooldown(display_frame, cooldown_message, cooldown_color, 
                                   cooldown_end_time, frame_start_time)
                    
                    # Show frame and continue
                    cv2.imshow('Hostel Biometric System', display_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                else:
                    # Cooldown period ended
                    cooldown_active = False
            
            # Only process every nth frame
            frame_count += 1
            if frame_count % process_every_n_frames != 0:
                cv2.imshow('Hostel Biometric System', display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Process frame for face recognition
            process_start_time = time.time()
            small_frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
            face_locations, face_names = recognize_faces(small_frame, known_face_encodings, known_face_names)
            
            # Scale face locations back to original size
            face_locations = [(int(top / 0.3), int(right / 0.3), int(bottom / 0.3), int(left / 0.3)) 
                             for top, right, bottom, left in face_locations]
            
            # Record processing time
            process_end_time = time.time()
            processing_times.append(process_end_time - process_start_time)
            
            # Process each detected face
            for i, (face_location, name) in enumerate(zip(face_locations, face_names)):
                top, right, bottom, left = face_location
                face_id = f"{left}_{top}_{right}_{bottom}"
                
                # Draw rectangle around face
                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                cv2.putText(display_frame, name, (left, top - 10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Handle face based on recognition result
                if name == "Unknown":
                    # Handle unknown face
                    cooldown_info, unknown_face_counters, known_face_encodings, known_face_names = handle_unknown_face(
                        video_capture, display_frame, face_id, face_location, unknown_face_counters, 
                        max_unknown_attempts, db_connected, students_collection, attendance_collection, 
                        voice_engine, cooldown_duration, known_face_encodings, known_face_names, last_entry_time
                    )
                    
                    if cooldown_info:
                        cooldown_active = cooldown_info["active"]
                        cooldown_end_time = cooldown_info["end_time"]
                        cooldown_message = cooldown_info["message"]
                        cooldown_color = cooldown_info["color"]
                else:
                    # Handle known face
                    cooldown_info, last_entry_time = handle_known_face(
                        face_location, name, db_connected, students_collection, attendance_collection, 
                        voice_engine, cooldown_duration, last_entry_time, min_entry_gap, display_frame
                    )
                    
                    if cooldown_info:
                        cooldown_active = cooldown_info["active"]
                        cooldown_end_time = cooldown_info["end_time"]
                        cooldown_message = cooldown_info["message"]
                        cooldown_color = cooldown_info["color"]
            
            # Clean up old face IDs periodically
            if frame_count % 50 == 0:
                unknown_face_counters = {}
            
            # Display the frame
            cv2.imshow('Hostel Biometric System', display_frame)
            
            # Check for exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Clean up
        video_capture.release()
        cv2.destroyAllWindows()
        
        # Signal speech thread to exit
        if voice_engine:
            speech_thread_running = False
            try:
                speech_queue.put("EXIT")
            except:
                pass

if __name__ == "__main__":
    main()
