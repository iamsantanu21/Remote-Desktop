import socket
import cv2
import pickle
import struct
import pyautogui

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))  # Listen on all interfaces
server_socket.listen(1)
print("Waiting for connection...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

while True:
    # Capture screen
    screenshot = pyautogui.screenshot()
    frame = cv2.cvtColor(cv2.array(screenshot), cv2.COLOR_RGB2BGR)

    # Encode image
    _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    data = pickle.dumps(encoded_frame)

    # Send size and data
    conn.sendall(struct.pack("Q", len(data)) + data)

    # Receive commands (optional)
    try:
        command = conn.recv(1024).decode()
        if command == "exit":
            break
    except:
        pass

conn.close()
server_socket.close()
