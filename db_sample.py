from pymongo import MongoClient

def get_db():

    #connecting to the MongoDB Compass server
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Hostel_Attendance"] #Database for all hostel related data
    attendance_collection = db["Attendance_records"] #collection to store attendance records

    return attendance_collection

if __name__ == "__main__":

    attendance_collection = get_db()
    #inserting a sample data:  
    test_data = {"Name": "Dev Mishra", "Roll No": 22053596, "Attendance": True, "Time of Attendance": "6:30pm"}
    attendance_collection.insert_one(test_data)
    print("Test document inserted successfully.")
