import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, db, storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://faceattendancerealtime-b1338-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "faceattendancerealtime-b1338.appspot.com"
})

# Importing the mode images into a list
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    # Add images to database
    fileName = f"{folderPath}/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]

file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File saved.")




