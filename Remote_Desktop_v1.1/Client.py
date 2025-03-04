import socket
import cv2
import pickle
import struct
import ssl
import pyautogui

# Connect to server
server_ip = "10.10.166.113"  # Replace with Windows server IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Secure connection
context = ssl.create_default_context()
conn = context.wrap_socket(client_socket, server_hostname=server_ip)
conn.connect((server_ip, 9999))
print("Connected to server.")

try:
    while True:
        # Receive frame size
        data_size = struct.unpack("Q", conn.recv(8))[0]

        # Receive image data
        data = b""
        while len(data) < data_size:
            data += conn.recv(4096)

        # Decode frame
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # Display the frame
        cv2.imshow("Live Remote Desktop", frame)

        # Send mouse position
        x, y = pyautogui.position()
        conn.sendall(f"MOUSE_MOVE {x} {y}".encode())

        # Press 'q' to exit
        if cv2.waitKey(1) == ord("q"):
            break
except Exception as e:
    print(f"Error: {e}")

conn.close()
cv2.destroyAllWindows()
