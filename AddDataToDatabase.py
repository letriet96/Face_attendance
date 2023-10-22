import firebase_admin
from firebase_admin import credentials, db


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendancerealtime-b1338-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Tạo ra thư mục Students trong database
ref = db.reference("Students")

data = {
    "321654":
        {
            "name": "Murtaza Hassan",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "852741":
        {
            "name": "Emily Blunt",
            "major": "Economics",
            "starting_year": 2018,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 2,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "avatar":
        {
            "name": "Le Huu Triet",
            "major": "computer science",
            "starting_year": 2022,
            "total_attendance": 1,
            "standing": "G",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

# Add data vào database với key nằm trong child và value trong set
for key, value in data.items():
    ref.child(key).set(value)








