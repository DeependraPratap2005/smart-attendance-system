from utils.liveness import check_blink
import cv2
import face_recognition
import pickle
import pandas as pd
from datetime import datetime
import os
import numpy as np

# LOAD MODEL
with open("trained_model/model.pkl", "rb") as f:
    data = pickle.load(f)

print("Students Loaded:", len(set(data["names"])))

cam = cv2.VideoCapture(0)

blink_verified = False

# SESSION DATA
try:
    with open("current_session.txt") as f:
        subject, faculty, slot, date = f.read().split("|")
except:
    print("Session Missing")
    exit()

file = "attendance/attendance.csv"

if not os.path.exists(file):
    df = pd.DataFrame(columns=[
        "Name","Date","Time","Subject","Faculty","Slot","Status"
    ])
    df.to_csv(file, index=False)

# PREMIUM LOOP
while True:

    ret, frame = cam.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # STATUS CHECK
    try:
        with open("attendance_status.txt") as f:
            flag = f.read().strip()
    except:
        flag = "OFF"

    if flag != "ON":
        cv2.putText(frame, "Attendance OFF", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)

        cv2.imshow("Smart Attendance Premium", frame)

        if cv2.waitKey(1) == 27:
            break
        continue

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # BLINK VERIFY
    if not blink_verified:
        if check_blink(frame):
            blink_verified = True
            print("Blink Verified")
        else:
            cv2.putText(frame, "Blink Eyes To Verify", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255), 2)

            cv2.imshow("Smart Attendance Premium", frame)

            if cv2.waitKey(1) == 27:
                break
            continue

    # FACE DETECT
    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)

    for (top, right, bottom, left), face_encoding in zip(faces, encodings):

        distances = face_recognition.face_distance(
            data["encodings"], face_encoding
        )

        best_match = np.argmin(distances)
        min_distance = distances[best_match]

        name = "Unknown"
        confidence = round((1 - min_distance) * 100, 2)

        if min_distance < 0.50:
            name = data["names"][best_match]

            now = datetime.now()
            time_now = now.strftime("%H:%M:%S")

            df = pd.read_csv(file)

            duplicate = df[
                (df["Name"] == name) &
                (df["Subject"] == subject) &
                (df["Slot"] == slot)
            ]

            if duplicate.empty:

                new_row = {
                    "Name": name,
                    "Date": date,
                    "Time": time_now,
                    "Subject": subject,
                    "Faculty": faculty,
                    "Slot": slot,
                    "Status": "Present"
                }

                df = pd.concat([df, pd.DataFrame([new_row])])
                df.to_csv(file, index=False)

                print(name, "Marked Present")

                cv2.putText(frame, "Attendance Marked",
                            (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0,255,0), 2)

            else:
                cv2.putText(frame, "Already Marked",
                            (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255,255,0), 2)

        # DRAW BOX
        color = (0,255,0) if name != "Unknown" else (0,0,255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        cv2.putText(frame,
                    f"{name} {confidence}%",
                    (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2)

    cv2.imshow("Smart Attendance Premium", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()

print("Recognition Closed")