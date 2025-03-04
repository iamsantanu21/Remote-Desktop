import socket
import cv2
import pickle
import struct
import pyautogui
import numpy as np
import threading
import time

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))  # Listen on all interfaces
server_socket.listen(5)  # Allow multiple connections
print("Waiting for connection...")

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            # Capture screen
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Resize frame to reduce data size (optional)
            frame = cv2.resize(frame, (1280, 720))  # Resize to 1280x720

            # Encode image
            _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            data = pickle.dumps(encoded_frame)

            # Send size and data
            conn.sendall(struct.pack("Q", len(data)) + data)

            # Add a small delay to control the frame rate
            time.sleep(0.05)  # ~20 FPS

            # Check for exit command
            try:
                command = conn.recv(1024).decode()
                if command == "exit":
                    break
            except:
                pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Connection closed: {addr}")

while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()