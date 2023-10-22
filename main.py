import os
import pickle
import cv2
import cvzone
import numpy as np
from face_recognition import compare_faces, face_distance, face_locations, face_encodings
from firebase_admin import db, credentials, storage
import firebase_admin
from datetime import datetime

"""
Một khi xác định được khuôn mặt, download data về người đó từ database rồi hiển thị thông tin đó trong vài giây, 
, rồi tới marked, rồi quay trở lại active mode, nếu người đó quay lại điểm danh lần nữa thì show cái already marked
"""
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendancerealtime-b1338-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "faceattendancerealtime-b1338.appspot.com"
})
bucket = storage.bucket()

cap = cv2.VideoCapture("http://10.195.169.243:8080//video")
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
file = open("EncodeFile.p", "rb")
encodeListWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListWithIds

modeType = 0  # để hiện thị mode (active, already mark v.v...)
counter = 0  # download info in the first frame
id = -1
imageStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, dsize=(640, 480))
    # imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Vị trí của khuôn mặt trong ảnh
    faces_coor = face_locations(imgS)  # faces_coor [(52, 498, 320, 230)] -> top, right, bottom, left
                                                                           # y1, x2, y2, x1

    # Phần camera bên trái
    imgBackground[162:162 + 480, 55:55 + 640] = imgS
    # Phần thông tin bên phải
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # Nếu có face trong frame
    if faces_coor:
        # mã hóa đặc trưng của khuôn mặt đó
        faces_encode = face_encodings(imgS, faces_coor)  # [np.array(128, )]

        # Xét từng khuôn mặt trong frame hiện tại
        for face_encode, face_coor in zip(faces_encode, faces_coor):
            # Đối chiếu gương mặt đang xét với cơ sở dữ liệu
            matches = compare_faces(encodeListKnown, face_encode, tolerance=0.6)  # [False, False, False]

            # Khoảng cách từ ảnh đang xét tới những ảnh trong cơ sở dữ liệu
            faceDis = face_distance(encodeListKnown, face_encode)  # [0.73016816 0.9170441  0.74644038]

            # Nếu nhận dạng được thì in ra thông tin
            match_idx = np.argmin(faceDis)
            if matches[match_idx]:
                y1, x2, y2, x1 = face_coor
                x1, y1, x2, y2 = x1 + 55, y1 + 162, x2 + 55, y2 + 162
                # bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1  # x1, y1, w, h
                # imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=1)
                imgBackground = cv2.rectangle(imgBackground, pt1=(x1, y1), pt2=(x2, y2), color=(0, 255, 0), thickness=1)
                id = studentIds[match_idx]

                # Một khi detect được thì chuyển counter từ 0 thành 1,
                # mode type cũng chuyển từ activate sang hiển thị data vừa down về
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1  # update the mode

        if counter != 0:
            # Tại frame đầu tiên
            if counter == 1:
                # Tải về thông tin gắn với id từ thư mục Students
                studentInfo = db.reference(f"Students/{id}").get()
                # Get the image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo["last_attendance_time"],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() -datetimeObject).total_seconds()

                if secondsElapsed > 30:
                    ref = db.reference(f"Students/{id}")
                    studentInfo["total_attendance"] += 1
                    ref.child("total_attendance").set(studentInfo["total_attendance"])
                    ref.child("last_attendance_time").set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if 10 < counter < 20:
                modeType = 2

            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter <= 10 and modeType == 1:
                cv2.putText(imgBackground, str(studentInfo["total_attendance"]), (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo["major"]), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo["standing"]), (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo["year"]), (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo["starting_year"]), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                (w, h), _ = cv2.getTextSize(str(studentInfo["name"]), cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2
                cv2.putText(imgBackground, str(studentInfo["name"]), (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (50, 50, 50), 1)

                imgBackground[175:175+216, 909:909+216] = imgStudent

            counter += 1

            # Reset
            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # Nếu không có face trong frame
    else:
        counter = 0
        modeType = 0

    cv2.imshow("Face attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


