import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
import requests
import base64
from datetime import datetime, timedelta

GITHUB_REPO = "IchigoSolos69/IRC"
CSV_FILE_PATH = "scanned_data.csv"
GITHUB_TOKEN = "<token>"

def initialize_csv():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        content = "QR Data,Count,Timestamp\n"
        encoded_content = base64.b64encode(content.encode()).decode()
        data = {
            "message": "Initialize CSV file",
            "content": encoded_content
        }
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 201:
            print("CSV file initialized.")
        else:
            print("Failed to initialize CSV file:", response.json())

def data_exists(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode()
        lines = content.splitlines()
        for line in lines[1:]:
            if data in line.split(",")[0]:
                return True, line.split(",")[1]  
    return False, None

def log_data_to_csv(data):
    exists, current_count, last_scanned_time = data_exists(data)
    if exists:
        last_scanned_dt = datetime.strptime(last_scanned_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        
        if current_time - last_scanned_dt >= timedelta(minutes=5):
            count = int(current_count) + 1
        else:
            print(f"QR code recently scanned. Last scanned at {last_scanned_time}.")
            return
    else:
        count = 1

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info["content"]).decode()
        updated_content = ""
        for line in content.splitlines():
            if line.split(",")[0] == data:
                updated_content += f"{data},{count},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            else:
                updated_content += line + "\n"
        if not exists:
            updated_content += f"{data},{count},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        encoded_content = base64.b64encode(updated_content.encode()).decode()
        update_data = {
            "message": "Update QR data",
            "content": encoded_content,
            "sha": file_info["sha"]
        }
        response = requests.put(url, headers=headers, json=update_data)
        if response.status_code == 200:
            print(f"Updated data: {data}, Count: {count}")
        else:
            print("Failed to update CSV file:", response.json())
    else:
        print("Error accessing CSV file:", response.json())

def data_exists(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CSV_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode()
        lines = content.splitlines()
        for line in lines[1:]:
            fields = line.split(",")
            if data == fields[0]:
                return True, fields[1], fields[2]
    return False, None, None

def main():
    initialize_csv()
    ip_camera_url = "http://100.85.131.159:8080/video"  # variable ip (needs to be changed everytime)
    cap = cv2.VideoCapture(ip_camera_url)

    cap.set(3, 320)
    cap.set(4, 240)

    if not cap.isOpened():
        print("Failed to access the camera feed.")
        return

    frame_count = 0
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to access the camera feed.")
            break

        frame_count += 1
        if frame_count % 2 == 0:
            for code in decode(img, symbols=[ZBarSymbol.QRCODE]):
                qr_data = code.data.decode('utf-8')
                log_data_to_csv(qr_data)

                print(f"Scanned QR Data: {qr_data}")

                pts = np.array([code.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 255, 0), 5)

                pts2 = code.rect
                cv2.putText(img, qr_data, (pts2[0], pts2[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("QR Scanner", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
