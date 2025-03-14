# Hostel Biometric System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-red.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green.svg)

A facial recognition-based attendance and access control system designed specifically for hostel environments. This system allows students to enter and exit the hostel multiple times per day using facial recognition, with manual fallback options.

## 📋 Features

### Core Functionality
- **Facial Recognition**: Identifies students using their facial features
- **Entry/Exit Tracking**: Records when students enter or leave the hostel
- **Multiple Entries**: Allows students to enter/exit multiple times per day
- **Manual Authorization**: Provides fallback for unrecognized faces
- **Face Registration**: Allows new students to register their faces

### Technical Features
- **Real-time Processing**: Optimized for smooth performance on standard hardware
- **Voice Feedback**: Provides audio confirmation using text-to-speech
- **Database Integration**: Stores all records in MongoDB for easy retrieval and analysis
- **Error Handling**: Robust error recovery for various failure scenarios
- **User-friendly Interface**: Clear visual feedback with status indicators

## 🚀 Recent Updates

- **Multiple Entry Support**: Students can now enter and exit multiple times per day (with a 60-second cooldown between scans)
- **Entry/Exit Tracking**: System now alternates between recording "Entry" and "Exit" events
- **Code Restructuring**: Completely modularized codebase for better maintainability
- **Performance Optimization**: Improved frame processing for smoother operation
- **Enhanced Error Handling**: Better recovery from face encoding failures
- **Visual Feedback Improvements**: Clearer status messages and countdown timers

## 🛠️ Technologies Used

- **Python**: Core programming language
- **OpenCV**: Computer vision and image processing
- **face_recognition**: Facial detection and recognition
- **MongoDB**: Database for storing student information and attendance records
- **pyttsx3**: Text-to-speech for voice feedback
- **Threading**: Multi-threaded processing for non-blocking operations

## 📦 Prerequisites

- Python 3.8 or higher
- MongoDB server running locally (default: localhost:27017)
- Webcam or USB camera
- The following Python packages:
  - opencv-python
  - face_recognition
  - pymongo
  - numpy
  - pyttsx3

## 💻 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/snehil-mod/Hostel_Biometric.git
   cd Hostel_Biometric
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv hostel_biometric_env
   # On Windows
   hostel_biometric_env\Scripts\activate
   # On macOS/Linux
   source hostel_biometric_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install opencv-python face_recognition pymongo numpy pyttsx3
   ```

4. **Start MongoDB** (if not already running):
   ```bash
   # This depends on your MongoDB installation
   # For Windows service:
   net start MongoDB
   ```

5. **Run the application**:
   ```bash
   python database_record.py
   ```

## 🔧 Configuration

The system is pre-configured with default settings, but you may need to adjust:

- **Database Connection**: Modify the MongoDB connection string in `get_db()` function if your MongoDB is not running on the default localhost:27017
- **Image Storage Path**: Update the path in `register_new_face()` and `load_face_encodings()` functions to match your environment
- **Entry Gap Time**: Adjust the `min_entry_gap` variable (default: 60 seconds) to change the minimum time between entries

## 📊 Database Structure

### Students Collection
- **Name**: Student's full name
- **Roll No**: Unique identifier
- **Face Registered**: Boolean indicating if face is registered

### Attendance Records Collection
- **Name**: Student's name
- **Roll No**: Student's roll number
- **Attendance**: Boolean (always true)
- **Date**: Date of entry/exit
- **Time of Attendance**: Time of entry/exit
- **Method**: "Facial Recognition" or "Manual ID"
- **Entry Type**: "Entry" or "Exit"

## 🎮 Usage

1. **Start the application**
2. **Face Recognition**:
   - Stand in front of the camera
   - The system will recognize registered faces and mark attendance
   - Green box: Recognized face
   - Red box: Unknown face

3. **Manual Authorization** (if face not recognized):
   - After 5 failed recognition attempts, the system will prompt for manual entry
   - Enter your roll number when prompted
   - Option to register your face for future recognition

4. **Exit the application**:
   - Press 'q' to quit

## 🧩 Code Structure

The application is organized into modular functions:

- **Speech Handling**: `init_voice_engine()`, `speak_text()`
- **Database Operations**: `get_db()`, `init_database()`, `record_attendance()`
- **Face Recognition**: `detect_faces()`, `recognize_faces()`, `load_face_encodings()`
- **User Management**: `verify_student_by_id()`, `manual_authorization()`, `register_new_face()`
- **Face Processing**: `handle_unknown_face()`, `handle_known_face()`
- **UI Elements**: `display_cooldown()`
- **Main Loop**: Contained in the `main()` function

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do almost anything they want with your project, like making and distributing closed source versions, as long as they provide attribution back to you and don't hold you liable.

## 📞 Contact

Snehil Singh - snehil.singh5151@gmail.com
Project Link: [https://github.com/yourusername/Hostel_Biometric](https://github.com/snehil-mod/Hostel_Biometric)

## 🙏 Acknowledgements

- [face_recognition](https://github.com/ageitgey/face_recognition)
- [OpenCV](https://opencv.org/)
- [MongoDB](https://www.mongodb.com/)
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
